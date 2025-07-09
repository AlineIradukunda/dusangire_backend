from django.db import models
from django.contrib.auth.models import AbstractUser

# ---------------------------
# MAIN MODELS
# ---------------------------

class School(models.Model):
    DELETE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Deletion'),
        ('deleted', 'Deleted'),
    ]

    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    AccountNumber = models.CharField(max_length=50, blank=True, null=True)
    

    # Soft delete fields
    delete_status = models.CharField(
        max_length=20,
        choices=DELETE_STATUS_CHOICES,
        default='active'
    )
    delete_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def total_received(self):
        return sum(d.amount for d in self.distributions.all())

class Distribution(models.Model):
    DELETE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('deleted', 'Deleted'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='distributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    distributed_on = models.DateTimeField(auto_now_add=True)
    delete_status = models.CharField(max_length=10, choices=DELETE_STATUS_CHOICES, default='active')
    delete_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.school.name} - {self.amount}"


class TransferReceived(models.Model):
    DELETE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Deletion'),
        ('deleted', 'Deleted'),
    ]

    SchoolCode = models.CharField(max_length=100, blank=True)
    Donor = models.CharField(max_length=200)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_type = models.CharField(
        max_length=50,
        choices=[
            ('local_transfer', 'Local Transfer'),
            ('momo', 'MoMo'),
            ('international_transfer', 'International Transfer'),
            ('lemitance', 'Lemitance')
        ],
        blank=True,
        null=True
    )
    SchoolName = models.ManyToManyField(School, blank=True)
    NumberOfTransactions = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # New fields for soft deletion
    delete_status = models.CharField(
        max_length=20,
        choices=DELETE_STATUS_CHOICES,
        default='active'
    )
    delete_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.SchoolCode or 'Anonymous'} - {self.Amount}"



class AdminUser(AbstractUser):
    is_super_admin = models.BooleanField(default=False)
    assigned_school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL)


class Report(models.Model):
    title = models.CharField(max_length=100)
    generated_on = models.DateTimeField(auto_now_add=True)
    total_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_distributed = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.generated_on.strftime('%Y-%m-%d')}"

