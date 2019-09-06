from django import forms
from .models import Application, Documents

class WaterApplicationForm(forms.Form):
    class Meta:
        model = Application
        fields = ['first_name','middle_initial','last_name','phone_number','email_address']

class DocumentUploadForm(forms.Form):
    class Meta:
        model = Documents
        fields = ['pay_period','income','residency_photo','income_photo']

    
