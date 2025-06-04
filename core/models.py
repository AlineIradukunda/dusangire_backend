from django.db import models
from django.contrib.auth.models import AbstractUser

class School(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def total_received(self):
        return sum(d.amount for d in self.distributions.all())

class Distribution(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='distributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    distributed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.amount}"

class TransferReceived(models.Model):
    DONOR_CHOICES = [
        ('METRO WORLD CHILD', 'METRO WORLD CHILD'),
        ('Indiv through MoMo', 'Indiv through MoMo'),
        ('IREMBO', 'IREMBO'),
        ('MTN RWANDACELL LTD', 'MTN RWANDACELL LTD')
    ]
    
    SchoolCode = models.CharField(max_length=100, blank=True)
    Donor = models.CharField(max_length=50, choices=DONOR_CHOICES)
    Total_Amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_type = models.CharField(max_length=50, choices=[('general', 'General'), ('specific', 'Specific')], default='general')
    SchoolName = models.ManyToManyField(School, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    AccountNumber = models.CharField(max_length=50, blank=True, null=True)
    NumberOfTransactions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.SchoolCode or 'Anonymous'} - {self.Total_Amount}"

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

