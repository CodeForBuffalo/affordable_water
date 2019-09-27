from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
from django.utils.translation import ugettext_lazy as _

class Application(models.Model):
    # HouseholdForm
    household_size = models.IntegerField(choices=(
            (1,_('Just me')),
            (2,_('2 people')),
            (3,_('3 people')),
            (4,_('4 people')),
            (5,_('5 people')),
            (6,_('6 people')),
            (7,_('7 people')),
            (8,_('8 people')),
        ), help_text=_("Typically how many people you regularly purchase and prepare food with, including yourself."))
    # AutoEligibleForm
    hasHouseholdBenefits = models.BooleanField()

    # Data from Income forms will be in a seperate model because 
    # if hasHouseholdBenefits is True, user won't have to enter income data
    annual_income = models.DecimalField(max_digits=11, decimal_places=2, blank=True, default=0, help_text=_("Must specify annual income if applicant does not have other household benefits (HEAP, SNAP, etc.)"))

    # ResidentInfoForm
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, blank=True)
    rent_or_own = models.CharField(max_length=4, choices=(
        ('rent',_("Rent")),
        ('own',_("Own")),
    ))

    # AddressForm
    street_address = models.CharField(max_length=200, validators=[RegexValidator(
        regex=r'^\d+ .*', message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ])
    apartment_unit = models.CharField(max_length=10, blank=True, help_text=_("Skip this if you don't live in an apartment"))
    zip_code = models.CharField(max_length=5, validators=[RegexValidator(
        regex=r'^\d{5}$', message=_("Your ZIP code must be exactly 5 digits"))
        ])

    # ContactInfoForm
    phone_number = models.CharField(max_length=12, validators=[ # validators should be a list
        RegexValidator(regex=r'^(\d{10}|(\d{3}\-\d{3}\-\d{4}))|(\(\d{3}\)\s?\d{3}\-\d{4})',
            message=_("Please use a valid phone number format such as 716-555-5555."))])
    email_address = models.EmailField(blank=True, help_text=_("Optional to provide for status updates on your application"))

    # account_holder in ResidentInfoForm
    account_holder = models.CharField(max_length=8, choices=[
        ('me',_("Me")),
        ('landlord',_("My landlord")),
        ('other',_("Another person")),
    ])

    # AccountHolderForm
    account_first = models.CharField(max_length=100)
    account_last = models.CharField(max_length=100)
    account_middle = models.CharField(max_length=5, blank=True)

    # AccountNumberForm
    account_number = models.CharField(max_length=30, validators=[ # validators should be a list
        RegexValidator(regex=r'^\d+$', message=_("Please enter only digits"))])

    # LegalForm
    legal_agreement = models.BooleanField()

    # SignatureForm
    signature = models.CharField(max_length=250)

    # Income Photo
    income_photo = models.ImageField(upload_to='income_docs', blank=True)

    def __str__(self):
        return f'{self.id} ({self.phone_number})'
