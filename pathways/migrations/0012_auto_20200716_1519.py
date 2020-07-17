# Generated by Django 2.2.14 on 2020-07-16 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathways', '0011_emailcommunication_historicalemailcommunication'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailcommunication',
            name='id',
        ),
        migrations.RemoveField(
            model_name='historicalemailcommunication',
            name='id',
        ),
        migrations.AlterField(
            model_name='emailcommunication',
            name='email_address',
            field=models.EmailField(editable=False, max_length=254, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='historicalemailcommunication',
            name='email_address',
            field=models.EmailField(db_index=True, editable=False, max_length=254),
        ),
    ]
