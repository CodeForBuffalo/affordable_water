from django.db import models
from django.core.validators import RegexValidator
from PIL import Image

# Create your models here.
class Application(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(blank=True, default='', max_length=5)
    last_name = models.CharField(max_length=100)

    phone_number = models.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        max_length=17, blank=True) # validators should be a list

    email_address = models.EmailField(blank=True)

class Documents(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    pay_period = models.CharField(choices=[
        ('WK',"Every week"),
        ('TWK',"Every two weeks"),
        ('TMO','Twice a month'),
        ('MO','Every month')],
        max_length=100)
    income = models.IntegerField()
    residency_photo = models.ImageField(upload_to='residency_docs')
    income_photo = models.ImageField(upload_to='income_docs')

class Account(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    # Account holder
    account_first = models.CharField(max_length=100)
    account_middle = models.CharField(blank=True, default='', max_length=5)
    account_last = models.CharField(max_length=100)

    # Account service address
    address_number = models.IntegerField()
    address_street = models.CharField(max_length=100)
    address_apartmentnum = models.CharField(max_length=100)
    address_zip = models.IntegerField()
    