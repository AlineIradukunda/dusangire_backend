from django.urls import path
from . import views


urlpatterns = [
    path('schools/', views.SchoolListCreateAPIView.as_view(), name='school-list'),
    path('contributions/', views.ContributionListCreateAPIView.as_view(), name='contribution-list'),
    path('admins/', views.AdminUserListAPIView.as_view(), name='admin-list'),
    path('simulate-payment/', views.SimulatePaymentAPIView.as_view(), name='simulate-payment'),
    path('distributions/', views.DistributionListAPIView.as_view(), name='distribution-list'),
    path('distribute/', views.DistributionCreateAPIView.as_view(), name='distribution-create'),
]
