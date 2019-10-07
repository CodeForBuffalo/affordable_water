from django import forms
from django.forms import ModelForm, widgets
from django.core.validators import RegexValidator
from .models import Application
from django.utils.translation import ugettext_lazy as _


class HouseholdForm(forms.Form):
    household = forms.ChoiceField(label=_("What is your household size?"),
        help_text=_("Typically how many people you regularly purchase and prepare food with, including yourself. If you live with them, include children under 22, spouses/partners, and parents."),
        choices=(
            (1,_('1')),
            (2,_('2')),
            (3,_('3')),
            (4,_('4')),
            (5,_('5')),
            (6,_('6')),
            (7,_('7')),
            (8,_('8+')),
        ), required=False)

class AutoEligibleForm(forms.Form):
    hasHouseholdBenefits = forms.ChoiceField(label=_("Does anyone in your household receive these benefits?"),
    choices=(
        (True,_('Yes')),
        (False,_('No')),
    ))

# Income Forms
class ExactIncomeForm(forms.Form):
    pay_period = forms.ChoiceField(choices=[
        ('weekly',_("Every week")),
        ('biweekly',_("Every two weeks")),
        ('semimonthly',_('Twice a month')),
        ('monthly',_('Every month')),
        ], label=_("How often do you get paid?"), required=False)
    income = forms.FloatField(min_value=0, label=_("How much money do you get each pay period before taxes?"))

    def __init__(self, *args, **kwargs):
        super(ExactIncomeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class HourlyIncomeForm(forms.Form):
    income = forms.FloatField(min_value=0, label=_("What is your hourly wage?"), label_suffix="")
    pay_period = forms.IntegerField(min_value=0, label=_("How many hours a week do you work?"), required=True)

    def __init__(self, *args, **kwargs):
        super(HourlyIncomeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class EstimateIncomeForm(forms.Form):
    income = forms.FloatField(min_value=0, label=_("How much money does your household make before taxes?"),
        label_suffix="", help_text=_("Include spouse and any children. Only include roommates if you purchase more than half of your meals together."))
    pay_period = forms.ChoiceField(choices=[
        ('weekly',_("Every week")),
        ('biweekly',_("Every two weeks")),
        ('semimonthly',_('Twice a month')),
        ('monthly',_('Every month')),
        ], label=_("How often?"), required=False)

    def __init__(self, *args, **kwargs):
        super(EstimateIncomeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

# End Income Forms

class ResidentInfoForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, label=_("What is your first name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("First name")}))
    last_name = forms.CharField(max_length=100, required=True, label=_("What is your last name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}))
    middle_initial = forms.CharField(max_length=5, required=False, label=_("What is your middle initial?"), 
        empty_value=(""))
    rent_or_own = forms.ChoiceField(choices=(
        ('rent',_("Rent")),
        ('own',_("Own")),
    ), required=True, label=_("Do you rent or own your home?"))
    account_holder = forms.ChoiceField(choices=[
        ('me',_("Me")),
        ('landlord',_("My landlord")),
        ('other',_("Another person")),
    ], required=True, label=_("Who is responsible for paying the water bill?"), 
    help_text=_("This is the name of the account holder listed on your water bill"))

class AddressForm(forms.Form):
    street_address = forms.CharField(max_length=200, label=_("What is your street address?"), validators=[RegexValidator(
        regex=r'^\d+ .*', message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ], widget=forms.TextInput(attrs={'placeholder': "123 Main St"}))
    apartment_unit = forms.CharField(required=False, max_length=10, label=_("If this is an apartment, what is the apartment unit?"), help_text=_("Skip this if you don't live in an apartment"))
    zip_code = forms.CharField(label=_("What is your 5 digit ZIP code?"), validators=[RegexValidator(
        regex=r'^\d{5}$', message=_("Your ZIP code must be exactly 5 digits")
    )])

class ContactInfoForm(forms.Form):
    phone_number = forms.CharField(label=_("What is your phone number?"), validators=[ # validators should be a list
        RegexValidator(regex=r'^(\d{10}|(\d{3}\-\d{3}\-\d{4}))|(\(\d{3}\)\s?\d{3}\-\d{4})',
            message=_("Please use a valid phone number format such as 716-555-5555."))],
        max_length=17, widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}))
    email_address = forms.EmailField(label=_("What is your email address?"), help_text=_("Optional to provide for status updates on your application"), required=False)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        phone = phone.replace('-','')
        phone = phone.replace('(','')
        phone = phone.replace(')','')
        phone = phone.replace(' ','')
        phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
        return phone

class AccountHolderForm(forms.Form):
    account_first = forms.CharField(max_length=100, required=True, label=_("What is the account holder's first name?"), widget=forms.TextInput(attrs={'placeholder': _("First name")}))
    account_last = forms.CharField(max_length=100, required=True, label=_("What is the account holder's last name?"), widget=forms.TextInput(attrs={'placeholder': _("Last name")}))
    account_middle = forms.CharField(max_length=5, required=False, label=_("What is the account holder's middle initial?"), empty_value=(""))

class AccountNumberForm(forms.Form):
    account_number = forms.CharField(label=_("What is your water account number?"), help_text=_("Your Buffalo Water account number can be found on your bill"), required=False)

class LegalForm(forms.Form):
    legal_agreement = forms.BooleanField(required=True, widget=widgets.CheckboxInput, label=_("I agree"), error_messages={
        'required': _("You must agree to the terms to continue"),})

class SignatureForm(forms.Form):
    signature = forms.CharField(max_length=250, required=True, label=_("Type your full legal name to sign this application"))

class DocumentIncomeForm(forms.Form):
    income_photo = forms.ImageField(label=_("Upload a pay stub from the last 30 days"), help_text=_("This is for any income you get from a job. If you are paid in cash, you can submit a letter from your employer."))

class DocumentHomeownerForm(forms.Form):
    residence_photo = forms.ImageField(label=_("Upload proof of your current residence status"), help_text=_("This can be any proof of ownership if you are the homeowner."))

class DocumentTenantForm(forms.Form):
    residence_photo = forms.ImageField(label=_("Upload proof of your current residence status"), help_text=_("This can be either a copy of your lease or a landlord statement showing that you (the tenant) are responsible for paying the water bill."))