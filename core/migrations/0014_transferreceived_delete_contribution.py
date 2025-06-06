# Generated by Django 5.2.1 on 2025-06-03 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_delete_adminreportspage_remove_momorecord_record_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferReceived',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SchoolCode', models.CharField(blank=True, max_length=100)),
                ('Donor', models.CharField(choices=[('Indiv through MoMo', 'Indiv through MoMo'), ('METRO WORLD CHILD', 'METRO WORLD CHILD'), ('IREMBO', 'IREMBO'), ('MTN RWANDACELL LTD', 'MTN RWANDACELL LTD')], max_length=50)),
                ('Total_Amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('contribution_type', models.CharField(choices=[('general', 'General'), ('specific', 'Specific')], default='general', max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('AccountNumber', models.CharField(max_length=50)),
                ('NumberOfPayments', models.IntegerField(default=0)),
                ('NumberOfTransactions', models.IntegerField(default=0)),
                ('SchoolName', models.ManyToManyField(blank=True, to='core.school')),
            ],
        ),
        migrations.DeleteModel(
            name='Contribution',
        ),
    ]
