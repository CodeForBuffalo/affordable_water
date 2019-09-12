from django import forms
from django.forms import ModelForm, widgets
from .models import Application, Document, Account
from django.utils.translation import ugettext_lazy as _

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
        phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
        return phone

class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['pay_period','income','residency_photo','income_photo']

class AccountForm(ModelForm):
    isAccountNameSame = forms.ChoiceField(required=True, initial=None, 
        label=_("Is your name listed on the water bill?"), 
        choices=(('-',"-"),(True,"Yes"),(False,"No")),
        widget=widgets.Select(attrs= {'onchange': ""}), # TODO add onchange function to hide account
        help_text=_("The person whose name is on the water bill. This might be a partner or roommate."))

    account_first = forms.CharField(max_length=100, required=False)
    account_middle = forms.CharField(max_length=5, required=False)
    account_last = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Account
        fields = ['isAccountNameSame','account_first','account_middle','account_last',
            'address_number','address_street','address_apartment_number','address_zip']
    
    # https://www.fusionbox.com/blog/detail/creating-conditionally-required-fields-in-django-forms/577/
    def fields_required(self, fields):
        """Used for conditionally marking fields as required."""
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError("This field is required.")
                self.add_error(field, msg)

    def clean(self):
        if self.cleaned_data.get('isAccountNameSame') == 'True':
            for field in ['account_first','account_middle','account_last']:
                self.fields[field].required = False
            app = Application.objects.filter(id=self.app_id)[0]
            self.cleaned_data['account_first'] = app.first_name
            self.cleaned_data['account_middle'] = app.middle_initial
            self.cleaned_data['account_last'] = app.last_name
        else:
            self.fields_required(['account_first','account_middle','account_last'])
        
        return self.cleaned_data

    # https://stackoverflow.com/questions/18605008/curious-about-get-form-kwargs-in-formview
    def __init__(self, *args, **kwargs):
        self.app_id = kwargs.pop('app_id', None)
        super(AccountForm, self).__init__(*args, **kwargs)

    
