from django.db import models
from django.core.validators import RegexValidator
from PIL import Image

# Create your models here.
class Application(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(blank=True, default='', max_length=5)
    last_name = models.CharField(max_length=100)

    phone_number = models.CharField(validators=[RegexValidator(regex=r'^(\d{10}|(\d{3}\-\d{3}\-\d{4}))|(\(\d{3}\)\s?\d{3}\-\d{4})',
        message="Please use a valid phone number format such as 716-555-5555.")],
        max_length=17) # validators should be a list
    # Validates for:
    # 7165555555
    # 716-333-4444
    # (716) 333-4444
    # (716)333-4444

    email_address = models.EmailField(blank=True)

    own_or_rent = models.CharField(max_length=5, default='Own', choices=(
        ('Own',"Own"),
        ('Rent',"Rent")
    ))

    def __str__(self):
        return f'{self.id} ({self.phone_number})'

class Document(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    pay_period = models.CharField(max_length=100, choices=[
        ('WK',"Every week"),
        ('TWK',"Every two weeks"),
        ('TMO','Twice a month'),
        ('MO','Every month')],
        )
    household = models.PositiveSmallIntegerField(default='1')
    income = models.PositiveIntegerField()
    residency_photo = models.ImageField(upload_to='residency_docs', blank=True)
    income_photo = models.ImageField(upload_to='income_docs', blank=True)

    def __str__(self):
        return f'{self.application.id} ({self.application.phone_number})'

class Account(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    # Account holder
    account_first = models.CharField(max_length=100)
    account_middle = models.CharField(blank=True, default='', max_length=5)
    account_last = models.CharField(max_length=100)

    # Account service address
    address_number = models.IntegerField()
    address_street = models.CharField(max_length=100)
    address_apartment_number = models.CharField(max_length=100, blank=True)
    address_zip = models.IntegerField()

    def __str__(self):
        return f'{self.application.id} ({self.application.phone_number})'
    