from django.urls import path
from . import views
from .views import (
    health_check,
    check_user_role_view,
    LoginAPIView,
    MyTokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # 🔹 Core Endpoints
    path('schools/', views.SchoolListCreateAPIView.as_view(), name='school-list'),
    path('transfers/', views.TransferReceivedListCreateAPIView.as_view(), name='transfer-list'),
    path('admins/', views.AdminUserListAPIView.as_view(), name='admin-list'),
    path('simulate-payment/', views.SimulatePaymentAPIView.as_view(), name='simulate-payment'),
    path('distributions/', views.DistributionListAPIView.as_view(), name='distribution-list'),
    path('distribute/', views.DistributionListCreateAPIView.as_view(), name='distribution-create'),

    path('reports/', views.ReportListCreateAPIView.as_view(), name='report-list'),
    path('transfers/upload/', views.TransferExcelUploadView.as_view(), name='transfer-upload'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate-report'),
    path('transaction-summary/', views.TransactionSummaryView.as_view(), name='transaction-summary'),

    # 🔹 Role & Auth
    path('check-role/', check_user_role_view, name='check-role'),
    path('login/', LoginAPIView.as_view(), name='custom-login'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('transfers/<int:pk>/delete/', views.mark_transfer_as_pending_delete, name='mark-transfer-delete'),
    path('transfers/<int:pk>/recover/', views.RecoverTransferView.as_view(), name='recover-transfer'),
    path("distributions/<int:pk>/delete/", views.MarkDistributionPendingDelete.as_view(), name="mark-distribution-pending-delete"),
    path("distributions/<int:pk>/confirm-delete/", views.ConfirmDistributionDeletion.as_view(), name="confirm-distribution-deletion"),
    path("distributions/<int:pk>/recover/", views.RecoverDistribution.as_view(), name="recover-distribution"),
    path("schools/<int:pk>/delete/", views.MarkSchoolPendingDeleteView.as_view(), name="school-delete"),
    path("schools/<int:pk>/recover/", views.RecoverSchoolView.as_view(), name="school-recover"),
    path("schools/<int:pk>/confirm/", views.ConfirmSchoolDeleteView.as_view(), name="school-confirm"),
    path("transfers/deleted/", views.deleted_transfers_list, name="deleted-transfers-list"),
    path("distributions/deleted/", views.deleted_distributions_list, name="deleted-distributions-list"),
    path("schools/deleted/", views.deleted_schools_list, name="deleted-schools-list"),
    # Confirm deletions
    path("transfers/<int:pk>/confirm/", views.ConfirmTransferDeleteView.as_view(), name="confirm-transfer-delete"),
    path("distributions/<int:pk>/confirm/", views.ConfirmDistributionDeletion.as_view(), name="confirm-distribution-delete"),




    # 🔹 Health Check
    path('health/', health_check, name='health_check'),
    # urls.py
]
