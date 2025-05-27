from rest_framework import serializers
from .models import School, Contribution, Distribution
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolSerializer(serializers.ModelSerializer):
    total_received = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = School
        fields = ['id', 'name', 'district', 'sector', 'created_at', 'total_received']


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ['id', 'contributor_name', 'payment_method', 'amount', 'timestamp']


class AdminUserSerializer(serializers.ModelSerializer):
    assigned_school_name = serializers.CharField(source='assigned_school.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'assigned_school', 'assigned_school_name']


class DistributionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Distribution
        fields = ['id', 'school', 'school_name', 'amount', 'distributed_on']

