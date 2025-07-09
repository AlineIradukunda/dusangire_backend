from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    School, TransferReceived, Distribution, Report,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 🔐 JWT Serializer with role
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user.is_superuser:
            role = "superuser"
        elif user.is_staff:
            role = "admin"
        else:
            role = "user"

        data['role'] = role
        data['username'] = user.username
        return data

User = get_user_model()

# 🔹 School Serializer with pending_deletion flag
class SchoolSerializer(serializers.ModelSerializer):
    total_received = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pending_deletion = serializers.SerializerMethodField()
    AccountNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = School
        fields = [
            'id', 'name', 'district', 'sector', 'created_at',
            'AccountNumber',
            'total_received', 'pending_deletion', 'delete_reason', 'delete_status'
        ]

    def get_pending_deletion(self, obj):
        return obj.delete_status == 'pending'

# 🔹 Admin User Serializer
class AdminUserSerializer(serializers.ModelSerializer):
    assigned_school_name = serializers.CharField(source='assigned_school.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'assigned_school', 'assigned_school_name']

# 🔹 Distribution Serializer with pending_deletion flag
class DistributionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Distribution
        fields = '__all__'

# 🔹 Report Serializer
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

# 🔹 Transfer Received Serializer with pending_deletion flag
class TransferReceivedSerializer(serializers.ModelSerializer):
    schools = SchoolSerializer(many=True, read_only=True, source='SchoolName')
    school_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    Donor = serializers.CharField()
    contribution_type = serializers.CharField(required=False, allow_null=True)
    pending_deletion = serializers.SerializerMethodField()

    class Meta:
        model = TransferReceived
        fields = [
            'id', 'SchoolCode', 'Donor', 'Amount', 'schools',
            'school_ids', 'NumberOfTransactions', 'timestamp',
            'contribution_type', 'pending_deletion', 'delete_status', 'delete_reason'
        ]

    def get_pending_deletion(self, obj):
        return obj.delete_status == 'pending'

    def validate_school_ids(self, value):
        if not School.objects.filter(id__in=value).count() == len(value):
            raise serializers.ValidationError("One or more school IDs are invalid.")
        return value

    def create(self, validated_data):
        school_ids = validated_data.pop('school_ids', [])
        transfer = TransferReceived.objects.create(**validated_data)
        if school_ids:
            transfer.SchoolName.set(school_ids)
        return transfer

    def update(self, instance, validated_data):
        school_ids = validated_data.pop('school_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if school_ids is not None:
            instance.SchoolName.set(school_ids)
        return instance
