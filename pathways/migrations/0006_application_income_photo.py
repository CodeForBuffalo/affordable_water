# Generated by Django 2.2.5 on 2019-09-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathways', '0005_auto_20190927_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='income_photo',
            field=models.ImageField(blank=True, upload_to='income_docs'),
        ),
    ]
