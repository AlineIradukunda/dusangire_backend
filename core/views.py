from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser  # Add this line
from django.contrib.auth import get_user_model
from openpyxl import load_workbook
from decimal import Decimal
import csv
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from datetime import datetime

from .models import School, TransferReceived, Distribution, Report
from .serializers import (
    SchoolSerializer, TransferReceivedSerializer, 
    DistributionSerializer, ReportSerializer, AdminUserSerializer
)
from .utils import generate_pdf_report

User = get_user_model()

# 🔹 School List/Create View
class SchoolListCreateAPIView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 🔹 Transfer List/Create View
class TransferReceivedListCreateAPIView(generics.ListCreateAPIView):
    queryset = TransferReceived.objects.all()
    serializer_class = TransferReceivedSerializer
    permission_classes = [permissions.AllowAny]


# 🔹 Admin Users List
class AdminUserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


# 🔹 Simulate MoMo Payment (For Testing)
class SimulatePaymentAPIView(APIView):
    def post(self, request):
        serializer = TransferReceivedSerializer(data=request.data)
        if serializer.is_valid():
            transfer = serializer.save()
            return Response({
                'message': 'Payment simulated successfully.',
                'data': TransferReceivedSerializer(transfer).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Distribution Create
class DistributionCreateAPIView(generics.CreateAPIView):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer


# 🔹 Distribution List
class DistributionListAPIView(generics.ListAPIView):
    queryset = Distribution.objects.all().order_by('-distributed_on')
    serializer_class = DistributionSerializer


# 🔹 Report List/Create
class ReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = Report.objects.all().order_by('-generated_on')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]


# 🔹 Upload Transfers from Excel
def clean_number(value):
    """Helper function to clean numeric values"""
    if not value:
        return '0'
    try:
        # Handle string representations with commas and spaces
        if isinstance(value, str):
            # Remove commas and spaces
            value = value.replace(',', '').replace(' ', '')
        # Convert to float first to handle Excel number formats
        float_val = float(str(value))
        # Return as integer string without decimals
        return str(int(float_val))
    except (ValueError, TypeError):
        return '0'

class TransferExcelUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wb = load_workbook(excel_file)
            ws = wb.active

            # Clean headers from the first row
            headers = [str(cell.value).lower().strip() if cell.value else '' for cell in ws[1]]

            required_columns = [
                'school_code', 'school_name', 'donor',
                'total_amount', 'account_number', 'number_of_transactions'
            ]

            # Check for missing headers
            missing_columns = [col for col in required_columns if col not in headers]
            if missing_columns:
                return Response({
                    'error': f'Missing required columns: {", ".join(missing_columns)}\n\n'
                             f'Expected columns: {", ".join(required_columns)}\n'
                             f'Found columns: {", ".join(headers)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            col_indices = {col: headers.index(col) for col in required_columns}

            errors = []
            transfers = []

            # Loop through Excel rows (skip header)
            for row_idx, row in enumerate(list(ws.rows)[1:], start=2):
                try:
                    donor_value = str(row[col_indices['donor']].value or '').strip()
                    school_name = str(row[col_indices['school_name']].value or '').strip()

                    # Find or create school
                    if school_name:
                        school, created = School.objects.get_or_create(
                            name=school_name,
                            defaults={'district': 'Unknown', 'sector': 'Unknown'}
                        )
                    else:
                        errors.append(f'Row {row_idx}: School name is required')
                        continue

                    # Clean and convert total amount
                    total_amount = row[col_indices['total_amount']].value
                    if total_amount:
                        try:
                            cleaned_amount = clean_number(total_amount)
                            total_amount = Decimal(cleaned_amount)
                        except (ValueError, TypeError, decimal.InvalidOperation):
                            errors.append(f'Row {row_idx}: Invalid amount format')
                            continue
                    else:
                        total_amount = Decimal('0')

                    # Handle account number
                    account_number = row[col_indices['account_number']].value
                    if account_number:
                        try:
                            account_number = clean_number(account_number)
                        except (ValueError, TypeError):
                            account_number = ''

                    transfer_data = {
                        'SchoolCode': str(row[col_indices['school_code']].value or '').strip(),
                        'Donor': donor_value,
                        'Total_Amount': total_amount,
                        'AccountNumber': account_number,
                        'NumberOfTransactions': int(float(clean_number(row[col_indices['number_of_transactions']].value or 0))),
                        'contribution_type': 'general'
                    }

                    serializer = TransferReceivedSerializer(data=transfer_data)
                    if serializer.is_valid():
                        transfer = serializer.save()
                        transfer.SchoolName.add(school)
                        transfers.append(transfer)
                    else:
                        errors.append(f'Row {row_idx}: {serializer.errors}')

                except (ValueError, TypeError, AttributeError) as e:
                    errors.append(f'Row {row_idx}: Invalid data format - {str(e)}')
                    continue

            response_data = {
                'message': f'Successfully created {len(transfers)} transfers',
                'transfers': TransferReceivedSerializer(transfers, many=True).data
            }

            if errors:
                response_data['warnings'] = errors

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Upload failed: {str(e)}")  # More detailed error logging
            return Response({
                'error': f'Error processing file: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Generate Report View
class GenerateReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        format_type = request.query_params.get('format', 'excel')

        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Query transfers within date range
        transfers = TransferReceived.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).order_by('timestamp')

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="report_{start_date.date()}_{end_date.date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Date', 'School Code', 'Donor', 'Amount', 'Account Number', 'School Names'])
            
            for transfer in transfers:
                writer.writerow([
                    transfer.timestamp.strftime('%Y-%m-%d %H:%M'),
                    transfer.SchoolCode,
                    transfer.Donor,
                    transfer.Total_Amount,
                    transfer.AccountNumber,
                    ', '.join(school.name for school in transfer.SchoolName.all())
                ])
            
            return response
        
        else:  # Excel format
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Add headers
            headers = ['Date', 'School Code', 'Donor', 'Amount', 'Account Number', 'School Names']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            # Add data rows
            for row, transfer in enumerate(transfers, 1):
                worksheet.write(row, 0, transfer.timestamp.strftime('%Y-%m-%d %H:%M'))
                worksheet.write(row, 1, transfer.SchoolCode)
                worksheet.write(row, 2, transfer.Donor)
                worksheet.write(row, 3, float(transfer.Total_Amount))
                worksheet.write(row, 4, transfer.AccountNumber)
                worksheet.write(row, 5, ', '.join(school.name for school in transfer.SchoolName.all()))

            workbook.close()
            output.seek(0)

            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="report_{start_date.date()}_{end_date.date()}.xlsx"'
            return response

# 🔹 Transaction Summary View
class TransactionSummaryView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            if start_date and end_date:
                transfers = TransferReceived.objects.filter(
                    timestamp__date__gte=start_date,
                    timestamp__date__lte=end_date
                )
            else:
                transfers = TransferReceived.objects.all()

            # Group by school and calculate totals
            summary = {}
            for transfer in transfers:
                for school in transfer.SchoolName.all():
                    if school.id not in summary:
                        summary[school.id] = {
                            'school_name': school.name,
                            'total_contributions': 0,
                            'total_distributed': school.total_received,
                        }
                    summary[school.id]['total_contributions'] += float(transfer.Total_Amount)

            # Convert to list and calculate balances
            summary_list = []
            for data in summary.values():
                data['balance'] = data['total_contributions'] - data['total_distributed']
                summary_list.append(data)

            return Response(summary_list)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
