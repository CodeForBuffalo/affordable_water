from django import forms
from django.forms import ModelForm
from .models import Application, Document, Account

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['first_name','middle_initial','last_name','phone_number','email_address']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        phone = phone.replace('-','')
        phone = phone.replace('(','')
        phone = phone.replace(')','')
        phone = phone.replace(' ','')
        country_code = '+1'
        if len(phone) > 10:
            country_code = phone[:-10]
            phone = phone[-10:]
        #phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
        phone = country_code + phone
        return phone

class DocumentUploadForm(ModelForm):
    class Meta:
        model = Document
        fields = ['pay_period','income','residency_photo','income_photo']

class AccountAddressForm(ModelForm):
    isAccountNameSame = forms.BooleanField(required=True, initial=False, label="Name on water bill", help_text="The person whose name is on the water bill. This might be a partner or roommate.")

    class Meta:
        model = Account
        fields = ['account_first','account_middle','account_last',
            'address_number','address_street','address_apartment_number','address_zip']

    
