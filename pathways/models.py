from django.db import models
from django.core.validators import RegexValidator
from PIL import Image

# Create your models here.
class Application(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(blank=True, default='')
    last_name = models.CharField(max_length=100)

    # https://www.codeproject.com/Questions/756671/convert-number-to-phone-number-format-using-java-s
    # https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-phone-number-in-django-models
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list

    email_address = models.EmailField(blank=True)

class Documents(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    pay_period = models.CharField(choices=[
        ('WK',"Every week"),
        ('TWK',"Every two weeks"),
        ('TMO','Twice a month'),
        ('MO','Every month')],
        )
    income = models.IntegerField()
    # pay stub or pay checks, any proof of other income
    residency_photo = models.ImageField(upload_to='residency_docs')
    income_photo = models.ImageField(upload_to='income_docs')

class Account(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    account_first = models.CharField(max_length=100)
    account_middle = models.CharField(blank=True, default='')
    account_last = models.CharField(max_length=100)

class Address(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    address_number = models.IntegerField()
    address_street = models.CharField()
    address_apartment = models.CharField()
    address_zip = models.IntegerField()