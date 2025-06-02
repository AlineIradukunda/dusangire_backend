from rest_framework import generics, permissions
from .models import School, Contribution, Distribution, Report
from .serializers import SchoolSerializer, ContributionSerializer, DistributionSerializer, ReportSerializer
from django.contrib.auth import get_user_model
from .serializers import AdminUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .utils import generate_pdf_report
from rest_framework.parsers import MultiPartParser, FormParser
from openpyxl import load_workbook
from decimal import Decimal


User = get_user_model()

# List all schools or create a new one
class SchoolListCreateAPIView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# List all contributions or create one
class ContributionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.AllowAny]


# Admin User List (optional: for admin panel)
class AdminUserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class SimulatePaymentAPIView(APIView):
    def post(self, request):
        data = request.data

        # Validate fields manually or use serializer
        serializer = ContributionSerializer(data=data)
        if serializer.is_valid():
            # Simulate "payment success"
            contribution = serializer.save()
            return Response({
                'message': 'Payment simulated successfully.',
                'data': ContributionSerializer(contribution).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DistributionCreateAPIView(generics.CreateAPIView):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer

# 🔹 View to list all distributions
class DistributionListAPIView(generics.ListAPIView):
    queryset = Distribution.objects.all().order_by('-distributed_on')
    serializer_class = DistributionSerializer

class ReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = Report.objects.all().order_by('-generated_on')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

class ContributionExcelUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Load workbook
            wb = load_workbook(excel_file)
            ws = wb.active
            
            # Get headers from first row
            headers = [cell.value.lower() if cell.value else '' for cell in ws[1]]
            required_columns = ['contributor_name', 'payment_method', 'amount', 'contribution_type']
            
            # Validate headers
            if not all(col in headers for col in required_columns):
                return Response({
                    'error': f'Excel file must contain these columns: {", ".join(required_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get column indices
            col_indices = {
                'contributor_name': headers.index('contributor_name'),
                'payment_method': headers.index('payment_method'),
                'amount': headers.index('amount'),
                'contribution_type': headers.index('contribution_type')
            }

            contributions = []
            # Start from second row (skip headers)
            for row in list(ws.rows)[1:]:
                try:
                    contribution_data = {
                        'contributor_name': row[col_indices['contributor_name']].value or '',
                        'payment_method': str(row[col_indices['payment_method']].value).lower(),
                        'amount': Decimal(str(row[col_indices['amount']].value)),
                        'contribution_type': str(row[col_indices['contribution_type']].value).lower(),
                    }

                    # Validate payment method
                    if contribution_data['payment_method'] not in ['momo', 'bank']:
                        continue

                    # Validate contribution type
                    if contribution_data['contribution_type'] not in ['general', 'specific']:
                        contribution_data['contribution_type'] = 'general'

                    serializer = ContributionSerializer(data=contribution_data)
                    if serializer.is_valid():
                        contribution = serializer.save()
                        contributions.append(contribution)
                except (ValueError, TypeError, AttributeError):
                    # Skip rows with invalid data
                    continue

            return Response({
                'message': f'Successfully created {len(contributions)} contributions',
                'contributions': ContributionSerializer(contributions, many=True).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Error processing file: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

