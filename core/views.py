from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from openpyxl import load_workbook
from decimal import Decimal

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

                    # Updated donor validation with exact matches
                    valid_donors = [
                        'Indiv through MoMo',
                        'METRO WORLD CHILD',
                        'IREMBO',
                        'MTN RWANDACELL LTD'
                    ]

                    # Case-insensitive donor matching
                    donor_match = next((d for d in valid_donors if d.lower() == donor_value.lower()), None)
                    if not donor_match:
                        errors.append(f'Row {row_idx}: Invalid donor value "{donor_value}". Must be one of: {", ".join(valid_donors)}')
                        continue
                    
                    donor_value = donor_match  # Use the correctly cased donor value

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
