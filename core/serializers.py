from rest_framework import serializers
from .models import School, Contribution, Distribution, Report
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolSerializer(serializers.ModelSerializer):
    total_received = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = School
        fields = ['id', 'name', 'district', 'sector', 'created_at', 'total_received']


class ContributionSerializer(serializers.ModelSerializer):
    schools = SchoolSerializer(many=True, read_only=True)
    school_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Contribution
        fields = ['id', 'contributor_name', 'payment_method', 'amount', 'contribution_type', 'schools', 'school_ids', 'timestamp']

    def create(self, validated_data):
        school_ids = validated_data.pop('school_ids', [])
        contribution = Contribution.objects.create(**validated_data)
        if school_ids:
            contribution.schools.set(school_ids)
        return contribution


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

class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = '__all__'

