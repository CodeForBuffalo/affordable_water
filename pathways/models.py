from django.db import models
from django.core.validators import RegexValidator, ValidationError
from PIL import Image
from django.utils.translation import ugettext_lazy as _
import magic
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from datetime import datetime
from simple_history.models import HistoricalRecords
from . import helpers

class Application(models.Model):
    # Metadata
    history = HistoricalRecords()

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
        ), help_text=_("Typically how many people you regularly share living expenses with, including yourself. If you live with them, include children under 21, spouses/partners, and parents."))
    # AutoEligibleForm
    has_household_benefits = models.BooleanField()

    # Data from Income forms will be in a seperate model because 
    # if has_household_benefits is True, user won't have to enter income data
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
    account_number = models.CharField(max_length=30, blank=True, validators=[ # validators should be a list
        RegexValidator(regex=r'^\d+$', message=_("Please enter only digits"))])

    # LegalForm
    legal_agreement = models.BooleanField()

    # SignatureForm
    signature = models.CharField(max_length=250)

    status = models.CharField(
        max_length=12, 
        choices=[
            ('new',_("New")),
            ('in_progress', _("In Progress")),
            ('enrolled',_("Enrolled")),
            ('denied',_("Denied")),
        ], 
        default='new')

    notes = models.TextField(
        blank=True,
        help_text="Enter any notes for this case",
        default='')

    def __str__(self):
        return f'{self.id} - {self.last_name} at {self.street_address}'

    @property
    def discount_amount(self):
        very_low_income_thresholds = helpers.getVeryLowIncomeThresholds()
        max_income = very_low_income_thresholds[self.household_size]
        return 90 if self.annual_income <= max_income else 60

    class Meta:
        verbose_name = 'Discount Application'
        verbose_name_plural = 'Discount Applications'

class EmailCommunication(models.Model):
    email_address = models.EmailField(primary_key=True, blank=False, null=False)
    discount_application_received = models.BooleanField(default=False)
    amnesty_application_received = models.BooleanField(default=False)
    enrolled_in_amnesty_program = models.BooleanField(default=False)
    enrolled_in_discount_program = models.BooleanField(default=False)

    # Metadata
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.email_address}'

@deconstructible
class FileValidator(object):
    """A class to validate a file with size and contents constraints

    Attributes
    ----------
    error_messages : dict
        dictionary with error messages for each constructor parameter

    Source: # https://stackoverflow.com/questions/20272579/django-validate-file-type-of-uploaded-file
    """
    error_messages = {
     'max_size': _("Ensure this file size is not greater than %(max_size)s."
                  " Your file size is %(size)s."),
     'min_size': _("Ensure this file size is not less than %(min_size)s. "
                  "Your file size is %(size)s."),
     'content_type': _("Files of type %(content_type)s are not supported."),
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        """
        Parameters
        ----------
        max_size : int
            optional maximum number of bytes
        min_size : int
            optional minimum number of bytes
        content_type : tuple
            tuple of content types in MIME form such as ('image/jpeg', 'application/pdf', )

        """
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size), 
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'],
                                   code='max_size', params=params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.min_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'], 
                                   code='min_size', params=params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)

            if content_type not in self.content_types:
                params = { 'content_type': content_type }
                raise ValidationError(self.error_messages['content_type'],
                                   code='content_type', params=params)

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator) and
            self.max_size == other.max_size and
            self.min_size == other.min_size and
            self.content_types == other.content_types
        )


def path_and_rename(instance, filename):
    """Renames and paths document file on upload

    The filename is based on the primary key of the document object.
    If the primary key does not exist, the filename is the current datetime.

    When this function is called, the document's content type 
    has already gone through 2 checks

        1) File extension is validated against accepted extensions (.jpeg, .png, etc)
        2) FileValidator checks the content of the file's header 
            (malicious code might be masked with an accepted extension)

    Parameters
    ----------
    instance : Document instance
        instance of Document object
    filename : str
        string of uploaded file
    
    Returns
    -------
    str
        Constructed path and name for file to upload to S3

    """
    upload_to = 'documents'
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = f'{instance.pk}'
    else:
        t = datetime.now()
        filename = f'{t.year}-{t.month}-{t.day}-{t.hour}-{t.minute}-{t.second}-{t.microsecond}'
    return f'{upload_to}/{filename}.{ext}'

# Validator for acceptable file uploads, used by both Document model and in forms.py
ACCEPTED_FILE_VALIDATOR = FileValidator(
    max_size=1024 * 4000, content_types=(
        'image/jpeg',
        'image/png',
        'application/pdf',
        'image/tiff',
        )
    )

class Document(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=9, choices=[
        ('income', _('Income')),
        ('benefits', _('Benefits')),
        ('residence', _('Residence'))
    ])
    doc_file = models.FileField(upload_to=path_and_rename, blank=True, validators=[ACCEPTED_FILE_VALIDATOR])
    
    # Metadata
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.application.id} - {self.application.last_name} at {self.application.street_address} - {self.doc_type}'

class ForgivenessApplication(models.Model):
    # Metadata
    history = HistoricalRecords()

    # ResidentInfoForm
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(
        max_length=5, 
        blank=True)

    # AddressForm
    street_address = models.CharField(
        max_length=200, 
        validators=[RegexValidator(
            regex=r'^\d+ .*', 
            message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ])
    apartment_unit = models.CharField(
        max_length=10, 
        blank=True, 
        help_text=_("Skip this if you don't live in an apartment"))
    zip_code = models.CharField(
        max_length=5, 
        validators=[RegexValidator(
            regex=r'^\d{5}$', 
            message=_("Your ZIP code must be exactly 5 digits"))
        ])

    # ContactInfoForm
    phone_number = models.CharField(
        max_length=12, 
        validators=[RegexValidator(
            regex=r'^(\d{10}|(\d{3}\-\d{3}\-\d{4}))|(\(\d{3}\)\s?\d{3}\-\d{4})',
            message=_("Please use a valid phone number format such as 716-555-5555."))
            ])

    email_address = models.EmailField(
        blank=True, 
        help_text=_("Optional to provide for status updates on your application"))

    status = models.CharField(
        max_length=12, 
        choices=[
            ('new',_("New")),
            ('in_progress', _("In Progress")),
            ('enrolled',_("Enrolled")),
            ('denied',_("Denied")),
        ], 
        default='new')

    notes = models.TextField(
        blank=True,
        help_text="Enter any notes for this case",
        default='')

    def __str__(self):
        return f'{self.id} - {self.last_name} at {self.street_address}'

    class Meta:
        verbose_name = 'Amnesty Application'
        verbose_name_plural = 'Amnesty Applications'

class Referral(models.Model):
    program = models.CharField(default='', max_length=60)
    facebook = models.BooleanField(default=False)
    google = models.BooleanField(default=False)
    twitter = models.BooleanField(default=False)
    linkedin = models.BooleanField(default=False)
    bill = models.BooleanField(default=False)
    ad = models.BooleanField(default=False)
    pamphlet = models.BooleanField(default=False)
    word_of_mouth = models.BooleanField(default=False)
    custom_referral = models.CharField(default='', max_length=60)