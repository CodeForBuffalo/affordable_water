from django import forms
from django.forms import ModelForm
from .models import Application, Documents, Account

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['first_name','middle_initial','last_name','phone_number','email_address']

class DocumentUploadForm(ModelForm):
    class Meta:
        model = Documents
        fields = ['pay_period','income','residency_photo','income_photo']

class AccountAddressForm(ModelForm):
    class Meta:
        model = Account
        fields = ['account_first','account_middle','account_last',
            'address_number','address_street','address_apartmentnum','address_zip']

    
