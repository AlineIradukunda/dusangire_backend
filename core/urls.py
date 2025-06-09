from django.urls import path
from . import views

urlpatterns = [
    path('schools/', views.SchoolListCreateAPIView.as_view(), name='school-list'),
    path('transfers/', views.TransferReceivedListCreateAPIView.as_view(), name='transfer-list'),
    path('admins/', views.AdminUserListAPIView.as_view(), name='admin-list'),
    path('simulate-payment/', views.SimulatePaymentAPIView.as_view(), name='simulate-payment'),
    path('distributions/', views.DistributionListAPIView.as_view(), name='distribution-list'),
    path('distribute/', views.DistributionCreateAPIView.as_view(), name='distribution-create'),
    path('reports/', views.ReportListCreateAPIView.as_view(), name='report-list'),
    path('transfers/upload/', views.TransferExcelUploadView.as_view(), name='transfer-upload'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate-report'),
    path('transaction-summary/', views.TransactionSummaryView.as_view(), name='transaction-summary'),
]

