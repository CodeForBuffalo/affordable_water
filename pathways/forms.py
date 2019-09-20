from django import forms
from django.forms import ModelForm, widgets
from django.core.validators import RegexValidator
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

class HouseholdForm(forms.Form):
    household = forms.ChoiceField(label="What is your household size?",
        help_text="Typically how many people you regularly purchase and prepare food with, including yourself.",
        choices=(
            (1,_('Just me')),
            (2,_('2 people')),
            (3,_('3 people')),
            (4,_('4 people')),
            (5,_('5 people')),
            (6,_('6 people')),
            (7,_('7 people')),
            (8,_('8 people')),
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
    first_name = forms.CharField(max_length=100, required=True, label=_("What is your first name?"))
    last_name = forms.CharField(max_length=100, required=True, label=_("What is your last name?"))
    middle_initial = forms.CharField(max_length=5, required=False, label=_("What is your middle initial?"), empty_value=(""))
    rent_or_own = forms.ChoiceField(choices=(
        ('rent',_("Rent")),
        ('own',_("Own")),
    ), required=True, label=_("Do you rent or own your home?"))
    account_holder = forms.ChoiceField(choices=(
        ('me',_("Me")),
        ('landlord',_("My landlord")),
        ('other',_("Another person")),
    ), required=True, label=_("Who is responsible for paying the water bill?"), 
    help_text=_("This is the name of the account holder listed on your water bill"))

class AccountHolderForm(forms.Form):
    account_first = forms.CharField(max_length=100, required=True, label=_("What is the account holder's first name?"))
    account_last = forms.CharField(max_length=100, required=True, label=_("What is the account holder's last name?"))
    account_middle = forms.CharField(max_length=5, required=False, label=_("What is the account holder's middle initial?"), empty_value=(""))

class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['residency_photo','income_photo']

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

    
