# Generated by Django 2.2.14 on 2020-07-31 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathways', '0013_auto_20200731_0834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcommunication',
            name='email_address',
            field=models.EmailField(max_length=254, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='historicalemailcommunication',
            name='email_address',
            field=models.EmailField(db_index=True, max_length=254),
        ),
    ]
