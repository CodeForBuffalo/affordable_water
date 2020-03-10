from django import forms
from django.forms import ModelForm, widgets
from django.core.validators import RegexValidator, ValidationError
from . import models
from django.utils.translation import ugettext_lazy as _


class HouseholdSizeForm(forms.Form):
    household_size = forms.ChoiceField(label=_("What is your household size?"),
        help_text=_("This is how many people you regularly share living expenses with, including yourself. If you live with them, include children, spouses/partners, and parents."),
        choices=(
            (1,_('1')),
            (2,_('2')),
            (3,_('3')),
            (4,_('4')),
            (5,_('5')),
            (6,_('6')),
            (7,_('7')),
            (8,_('8+')),
        ), required=True)

    def __init__(self, *args, **kwargs):
        super(HouseholdSizeForm, self).__init__(*args, **kwargs)
        self.fields['household_size'].error_messages = {'required': _("Select your household size.")}

class HouseholdBenefitsForm(forms.Form):
    has_household_benefits = forms.ChoiceField(label=_("Does anyone in your household receive these benefits?"),
    choices=(
        (True,_('Yes')), (False,_('No')),
    ), help_text=_("Supplemental Nutrition Assistance Program (SNAP/Food Stamps), Home Energy Assistance Program (HEAP), Supplemental Security Income (SSI), Public Assistance"))

class HouseholdContributorsForm(forms.Form):
    household_contributors = forms.ChoiceField(label=_("How many individuals contribute to your household income?"),
    choices=(
        (1,_('1')), (2,_('2')), (3,_('3')), (4,_('4')),
        (5,_('5')), (6,_('6')), (7,_('7')), (8,_('8+')),
    ), help_text=_("Include anyone who regularly contributes to your household living expenses such as groceries, rent or property taxes, or utilities."))

class JobStatusForm(forms.Form):
    has_job = forms.ChoiceField(label=_("Do you have a job?"),
    choices=(
        (True,_('Yes')), (False,_('No')),
    ), help_text=_("Make sure to include self-employed work."))

    def __init__(self, *args, **kwargs):
        super(JobStatusForm, self).__init__(*args, **kwargs)
        self.fields['has_job'].error_messages = {'required': _("Select your employment status.")}

class SelfEmploymentForm(forms.Form):
    is_self_employed = forms.ChoiceField(label=_("Do you have income from freelance, independent contractor, or self-employment work?"),
    choices=(
        (True, _('Yes')), (False, _('No')),
    ))

    def __init__(self, *args, **kwargs):
        super(SelfEmploymentForm, self).__init__(*args, **kwargs)
        self.fields['is_self_employed'].error_messages = {'required': _("Select your self-employment status.")}

class OtherIncomeSourcesForm(forms.Form):
    has_other_income = forms.ChoiceField(label=_("Do you get any money from other sources?"), 
    choices=(
        (True, _('Yes')),(False, _('No')),
    ))

    def __init__(self, *args, **kwargs):
        super(OtherIncomeSourcesForm, self).__init__(*args, **kwargs)
        self.fields['has_other_income'].error_messages = {'required': _("Indicate whether you get any money from other sources.")}

class NumberOfJobsForm(forms.Form):
    number_of_jobs = forms.ChoiceField(label=_("In total, how many jobs do you have?"), 
    choices=(
            (1,_('1')),(2,_('2')),(3,_('3')),(4,_('4')),(5,_('5')),(6,_('6')),
            (7,_('7')),(8,_('8')),(9,_('9')),(10,_('10')),(11,_('11')),(12,_('12')),
        ))

    def __init__(self, *args, **kwargs):
        super(NumberOfJobsForm, self).__init__(*args, **kwargs)
        self.fields['number_of_jobs'].error_messages = {'required': _("Select how many jobs you currently have.")}

class NonJobIncomeForm(forms.Form):
    non_job_income = forms.FloatField(min_value=0, label=_("How much money from other sources do you get every month?"))

    def __init__(self, *args, **kwargs):
        super(NonJobIncomeForm, self).__init__(*args, **kwargs)
        self.fields['non_job_income'].error_messages = {'required': _("Be sure to provide your income from other sources.")}

# Income Forms
pay_period_choices = [
    ('weekly',_("Every week")),
    ('biweekly',_("Every two weeks")),
    ('semimonthly',_('Twice a month')),
    ('monthly',_('Every month')),
    ('annually',_('Every year')),
    ]

class IncomeMethodsForm(forms.Form):
    income_method = forms.ChoiceField(choices=[
        ('exact', _("I can provide the exact amount")),
        ('hourly', _("I can provide my hourly wage")),
        ('estimate', _("I can only provide an estimate")),
    ], label=_("What’s the best way to provide your household's pre-tax earnings from the last 30 days?"))


class ExactIncomeForm(forms.Form):
    pay_period = forms.ChoiceField(choices=pay_period_choices, label=_("How often do you get paid?"), required=True)
    income = forms.FloatField(min_value=0, label=_("How much money do you get each pay period before taxes?"),
        help_text=_("If this changes with each pay period, average the pay amounts for the last 30 days."))

    def __init__(self, *args, **kwargs):
        super(ExactIncomeForm, self).__init__(*args, **kwargs)
        self.fields['income'].error_messages = {'required': _("Be sure to provide your income before taxes")}
        self.fields['pay_period'].error_messages = {'required': _("Select a pay period")}


class HourlyIncomeForm(forms.Form):
    income = forms.FloatField(min_value=0.01, label=_("What is your hourly wage?"), label_suffix="")
    pay_period = forms.IntegerField(min_value=1, max_value=168, label=_("How many hours a week do you work?"), required=True, 
        help_text=_("If this changes, give an average for the last 30 days."))

    def __init__(self, *args, **kwargs):
        super(HourlyIncomeForm, self).__init__(*args, **kwargs)
        self.fields['income'].error_messages = {'required': _("Be sure to provide an hourly wage.")}
        self.fields['pay_period'].error_messages = {'required': _("Be sure to provide hours a week.")}


class EstimateIncomeForm(forms.Form):
    income = forms.FloatField(min_value=0, label=_("How much money does your household make before taxes?"),
        label_suffix="", help_text=_("Include anyone who contributes to paying living expenses."))
    pay_period = forms.ChoiceField(choices=pay_period_choices, label=_("How often?"), required=True)
    
    def __init__(self, *args, **kwargs):
        super(EstimateIncomeForm, self).__init__(*args, **kwargs)
        self.fields['income'].error_messages = {'required': _("Be sure to provide a household income.")}
        self.fields['pay_period'].error_messages = {'required': _("Select how often your household makes this amount.")}

# End Income Forms

class ResidentInfoForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, label=_("What is your first name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("First name")}), help_text=_("Legally as it appears on your ID."))
    last_name = forms.CharField(max_length=100, required=True, label=_("What is your last name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}), help_text=_("Legally as it appears on your ID."))
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

    def __init__(self, *args, **kwargs):
        super(ResidentInfoForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].error_messages = {'required': _("Make sure to provide a first name.")}
        self.fields['last_name'].error_messages = {'required': _("Make sure to provide a last name.")}
        self.fields['rent_or_own'].error_messages = {'required': _("Make sure to indicate whether you own or rent.")}
        self.fields['account_holder'].error_messages = {'required': _("Make sure to indicate who officially pays the water bill.")}
    

class AddressForm(forms.Form):
    street_address = forms.CharField(max_length=200, label=_("What is your street address?"), validators=[RegexValidator(
        regex=r'^\d+ .*', message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ], widget=forms.TextInput(attrs={'placeholder': "123 Main St"}))
    apartment_unit = forms.CharField(required=False, max_length=10, label=_("If this is an apartment, what is the apartment unit?"), help_text=_("Skip this if you don't live in an apartment"))
    zip_code = forms.CharField(label=_("What is your 5 digit ZIP code?"), validators=[RegexValidator(
        regex=r'^\d{5}$', message=_("Your ZIP code must be exactly 5 digits")
    )])

    card_title = _("Where are you currently living?")

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['street_address'].error_messages = {'required': _("Make sure to provide a street address.")}
        self.fields['zip_code'].error_messages = {'required': _("Make sure to provide a 5 digit ZIP code.")}

class ContactInfoForm(forms.Form):
    phone_number = forms.CharField(label=_("What is your phone number?"),
        max_length=17, widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}))
    email_address = forms.EmailField(label=_("What is your email address?"), help_text=_("Please provide if you wish to receive status updates on your application."), required=False)

    card_title = _("Okay, let's get your contact info.")

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        phone = phone.replace('-','')
        phone = phone.replace('(','')
        phone = phone.replace(')','')
        phone = phone.replace(' ','')
        if len(phone) != 10:
            raise ValidationError(_("Please use a valid 10 digit phone number such as 716-555-5555."), code='invalid')
        phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
        return phone

    def __init__(self, *args, **kwargs):
        super(ContactInfoForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].error_messages = {'required': _("Make sure to provide a valid phone number.")}

class AccountHolderForm(forms.Form):
    account_first = forms.CharField(max_length=100, required=True, label=_("What is the account holder's first name?"), widget=forms.TextInput(attrs={'placeholder': _("First name")}))
    account_last = forms.CharField(max_length=100, required=True, label=_("What is the account holder's last name?"), widget=forms.TextInput(attrs={'placeholder': _("Last name")}))
    account_middle = forms.CharField(max_length=5, required=False, label=_("What is the account holder's middle initial?"), empty_value=(""))

    card_title = _("Whose name is officially on your water bill?")

    def __init__(self, *args, **kwargs):
        super(AccountHolderForm, self).__init__(*args, **kwargs)
        self.fields['account_first'].error_messages = {'required': _("Make sure to provide a first name.")}
        self.fields['account_last'].error_messages = {'required': _("Make sure to provide a last name.")}

class AccountNumberForm(forms.Form):
    account_number = forms.CharField(label=_("What is your water account number?"), help_text=_("Your Buffalo Water account number can be found on your bill"), required=False)
    has_account_number = forms.BooleanField(required=False, widget=forms.HiddenInput())
    card_title = _("Almost done! Let's get info on your water account.")


class LegalForm(forms.Form):
    legal_agreement = forms.BooleanField(required=True, widget=widgets.CheckboxInput, label=_("I agree"), error_messages={
        'required': _("You must agree to the terms to continue"),})

class SignatureForm(forms.Form):
    signature = forms.CharField(max_length=250, required=True, label=_("Type your full legal name to sign this application"), error_messages={'required':_("You must sign the application to continue.")})

class DocumentForm(forms.Form):
    doc = forms.FileField(validators=[models.ACCEPTED_FILE_VALIDATOR], required=False)

class LaterDocumentsForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, label=_("What is your first name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("First name")}), help_text=_("Legally as it appears on your ID."))
    last_name = forms.CharField(max_length=100, required=True, label=_("What is your last name?"), 
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}), help_text=_("Legally as it appears on your ID."))
    middle_initial = forms.CharField(max_length=5, required=False, label=_("What is your middle initial?"), 
        empty_value=(""), help_text=_("Optional"))
    zip_code = forms.CharField(label=_("What is your 5 digit ZIP code?"), validators=[RegexValidator(
        regex=r'^\d{5}$', message=_("Your ZIP code must be exactly 5 digits")
    )])
    phone_number = forms.CharField(label=_("What is your phone number?"),
        max_length=17, widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}))
    email_address = forms.EmailField(label=_("What is your email address?"), help_text=_("Optional"), required=False)
    card_title = _("Before submitting your documents, we need to match your information to an existing application.")

class MoreDocumentInfoRequiredForm(forms.Form):
    rent_or_own = forms.ChoiceField(choices=(
        ('rent',_("Rent")),
        ('own',_("Own")),
    ), required=True, label=_("Do you rent or own your home?"))
    apartment_unit = forms.CharField(required=False, max_length=10, label=_("If this is an apartment, what is the apartment unit?"), help_text=_("Skip this if you don't live in an apartment"))
    street_address = forms.CharField(max_length=200, label=_("What is your street address?"), validators=[RegexValidator(
        regex=r'^\d+ .*', message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ], widget=forms.TextInput(attrs={'placeholder': "123 Main St"}))
    household_size = forms.ChoiceField(label=_("What is your household size?"),
        help_text=_("Typically how many people you regularly share living expenses with, including yourself. If you live with them, include children under 21, spouses/partners, and parents."),
        choices=(
            (1,_('1')),
            (2,_('2')),
            (3,_('3')),
            (4,_('4')),
            (5,_('5')),
            (6,_('6')),
            (7,_('7')),
            (8,_('8+')),
        ), required=True)
    card_title = _("We need more information to find your existing application.")
