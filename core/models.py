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

class Contribution(models.Model):
    contributor_name = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, choices=[('momo', 'MoMo'), ('bank', 'Bank')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_type = models.CharField(max_length=50, choices=[('general', 'General'), ('specific', 'Specific')], default='general')
    schools = models.ManyToManyField(School, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contributor_name or 'Anonymous'} - {self.amount}"

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

