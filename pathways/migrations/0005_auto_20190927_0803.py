# Generated by Django 2.2.5 on 2019-09-27 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathways', '0004_application_annual_income'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='residency_photo',
        ),
        migrations.AlterField(
            model_name='application',
            name='annual_income',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Must specify annual income if applicant does not have other household benefits (HEAP, SNAP, etc.)', max_digits=11),
        ),
    ]
