# Generated by Django 2.2.14 on 2020-10-23 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathways', '0015_merge_20200731_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(default='', max_length=60)),
                ('facebook', models.BooleanField(default=False)),
                ('google', models.BooleanField(default=False)),
                ('twitter', models.BooleanField(default=False)),
                ('linkedin', models.BooleanField(default=False)),
                ('bill', models.BooleanField(default=False)),
                ('ad', models.BooleanField(default=False)),
                ('pamphlet', models.BooleanField(default=False)),
                ('word_of_mouth', models.BooleanField(default=False)),
                ('custom_referral', models.CharField(default='', max_length=60)),
            ],
        ),
    ]
