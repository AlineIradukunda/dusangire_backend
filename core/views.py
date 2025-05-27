from rest_framework import generics, permissions
from .models import School, Contribution, Distribution
from .serializers import SchoolSerializer, ContributionSerializer, DistributionSerializer
from django.contrib.auth import get_user_model
from .serializers import AdminUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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