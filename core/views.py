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

                    # Validate donor value
                    if donor_value not in ['Indiv through MoMo', 'METRO WORLD CHILD', 'IREMBO', 'MTN RWANDACELL LTD']:
                        errors.append(f'Row {row_idx}: Invalid donor value.')
                        continue

                    # Find or create school
                    if school_name:
                        school, created = School.objects.get_or_create(
                            name=school_name,
                            defaults={'district': 'Unknown', 'sector': 'Unknown'}
                        )
                    else:
                        errors.append(f'Row {row_idx}: School name is required')
                        continue

                    # Add account number handling
                    account_number = row[col_indices['account_number']].value
                    if account_number:
                        try:
                            account_number = str(int(float(str(account_number))))
                        except (ValueError, TypeError):
                            account_number = ''  # Allow blank values
                    else:
                        account_number = ''  # Keep it blank if no value

                    transfer_data = {
                        'SchoolCode': str(row[col_indices['school_code']].value or '').strip(),
                        'Donor': donor_value,
                        'Total_Amount': Decimal(str(row[col_indices['total_amount']].value or 0)),
                        'AccountNumber': account_number,  # Pass through blank values
                        'NumberOfTransactions': int(float(str(row[col_indices['number_of_transactions']].value or 0))),
                        'contribution_type': 'general'  # 🔹 Add default value
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
            print(f"Upload failed: {e}")  # Optional debug log
            return Response({
                'error': f'Error processing file: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
