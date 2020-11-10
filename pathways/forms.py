from django import forms
from django.forms import ModelForm, widgets
from django.core.validators import RegexValidator, ValidationError
from django.utils.translation import ugettext_lazy as _

from pathways.models import Referral, ACCEPTED_FILE_VALIDATOR

def getIntTuplesInclusive(start, end, appendPlusOnLast):
    result = []
    for x in range(start, end):
        pair = (x, _(str(x)))
        result.append(pair)

    if appendPlusOnLast:
        last = (end, _(str(end)+'+'))
    else:
        last = (end, _(str(end)))
    result.append(last)
    return result

def cleanPhoneNumberFormat(form):
    phone = form.cleaned_data.get('phone_number')
    phone = phone.replace('-','')
    phone = phone.replace('(','')
    phone = phone.replace(')','')
    phone = phone.replace(' ','')
    if len(phone) != 10:
        raise ValidationError(_("Please use a valid 10 digit phone number such as 716-555-5555."), code='invalid')
    phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
    return phone

class CityResidentForm(forms.Form):
    city_resident = forms.ChoiceField(
        label=_("Are you a City of Buffalo resident?"),
        help_text=_("The City of Buffalo does not include suburban municipalities "
                    "like Cheektowaga, Lackawanna, Amherst, or Tonawanda."),
        choices=((True,_('Yes')),(False,_('No')))
    )

class HouseholdSizeForm(forms.Form):
    HOUSEHOLD_SIZE_CHOICES = getIntTuplesInclusive(1, 8, True)

    household_size = forms.ChoiceField(
        label=_("What is your household size?"),
        help_text=_("This is how many people you regularly share living expenses with, including yourself. "
                    "If you live with them, include children, spouses/partners, and parents."),
        required=True,
        error_messages={'required': _("Select your household size.")},
        choices=HOUSEHOLD_SIZE_CHOICES
    )


class HouseholdBenefitsForm(forms.Form):
    has_household_benefits = forms.ChoiceField(
        label=_("Does anyone in your household receive these benefits?"),
        choices=((True,_('Yes')), (False,_('No'))),
        help_text=_("Supplemental Nutrition Assistance Program (SNAP/Food Stamps), "
                    "Home Energy Assistance Program (HEAP), Supplemental Security Income (SSI), Public Assistance")
    )

class HouseholdContributorsForm(forms.Form):
    HOUSEHOLD_CONTRIBUTOR_CHOICES = getIntTuplesInclusive(1, 8, True)

    household_contributors = forms.ChoiceField(
        label=_("How many individuals contribute to your household income?"),
        help_text=_("Include anyone who regularly contributes to your household living expenses "
                    "such as groceries, rent or property taxes, or utilities."),
        choices=(HOUSEHOLD_CONTRIBUTOR_CHOICES)
    )

class JobStatusForm(forms.Form):
    has_job = forms.ChoiceField(
        label=_("Do you have a job?"),
        help_text=_("Make sure to include self-employed work."),
        choices=((True,_('Yes')), (False,_('No'))),
        error_messages={'required': _("Select your employment status.")}
    )


class SelfEmploymentForm(forms.Form):
    is_self_employed = forms.ChoiceField(
        label=_("Do you have income from freelance, independent contractor, or self-employment work?"),
        choices=((True, _('Yes')), (False, _('No'))),
        error_messages={'required': _("Select your self-employment status.")}
    )


class OtherIncomeSourcesForm(forms.Form):
    has_other_income = forms.ChoiceField(
        label=_("Do you get any money from other sources?"), 
        choices=((True, _('Yes')),(False, _('No')),),
        error_messages={'required': _("Indicate whether you get any money from other sources.")}
    )


class NumberOfJobsForm(forms.Form):
    NUMBER_OF_JOBS_CHOICES = getIntTuplesInclusive(1, 12, False)

    number_of_jobs = forms.ChoiceField(
        label=_("In total, how many jobs do you have?"), 
        choices=NUMBER_OF_JOBS_CHOICES,
        error_messages={'required': _("Select how many jobs you currently have.")}
    )


class NonJobIncomeForm(forms.Form):
    non_job_income = forms.FloatField(
        label=_("How much money from other sources do you get every month?"),
        min_value=0,
        error_messages={'required': _("Be sure to provide your income from other sources.")}
    )


# Income Forms
PAY_PERIOD_CHOICES = [
    ('weekly',_("Every week")),
    ('biweekly',_("Every two weeks")),
    ('semimonthly',_('Twice a month')),
    ('monthly',_('Every month')),
    ('annually',_('Every year')),
]

class IncomeMethodsForm(forms.Form):
    income_method = forms.ChoiceField(
        label=_("What’s the best way to provide your household's pre-tax earnings from the last 30 days?"),
        choices=[
            ('exact', _("I can provide the exact amount")),
            ('hourly', _("I can provide my hourly wage")),
            ('estimate', _("I can only provide an estimate")),
        ]
    )


class ExactIncomeForm(forms.Form):
    pay_period = forms.ChoiceField(
        label=_("How often do you get paid?"),
        required=True,
        choices=PAY_PERIOD_CHOICES,
        error_messages = {'required': _("Select a pay period")}
    )

    income = forms.FloatField(
        label=_("How much money do you get each pay period before taxes?"),
        help_text=_("If this changes with each pay period, average the pay amounts for the last 30 days."),
        min_value=0,
        error_messages={'required': _("Be sure to provide your income before taxes")}
    )


class HourlyIncomeForm(forms.Form):
    income = forms.FloatField(
        label=_("What is your hourly wage?"),
        label_suffix="",
        min_value=0.01,
        error_messages={'required': _("Be sure to provide an hourly wage.")}
    )

    pay_period = forms.IntegerField(
        label=_("How many hours a week do you work?"),
        help_text=_("If this changes, give an average for the last 30 days."),
        min_value=1, 
        max_value=168, 
        required=True,
        error_messages={'required': _("Be sure to provide hours a week.")}
    )


class EstimateIncomeForm(forms.Form):
    income = forms.FloatField(
        label=_("How much money does your household make before taxes?"),
        label_suffix="",
        help_text=_("Include anyone who contributes to paying living expenses."),
        min_value=0,
        error_messages={'required': _("Be sure to provide a household income.")}
    )

    pay_period = forms.ChoiceField(
        label=_("How often?"),
        required=True,
        choices=PAY_PERIOD_CHOICES,
        error_messages={'required': _("Select how often your household makes this amount.")}
    )
    
# End Income Forms

class ResidentInfoForm(forms.Form):
    ACCOUNT_HOLDER_CHOICES = [
        ('me',_("Me")),
        ('landlord',_("My landlord")),
        ('other',_("Another person")),
    ]

    first_name = forms.CharField(
        label=_("What is your first name?"),
        help_text=_("Legally as it appears on your ID."),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _("First name")}),
        error_messages={'required': _("Make sure to provide a first name.")}
    )

    last_name = forms.CharField(
        label=_("What is your last name?"), 
        help_text=_("Legally as it appears on your ID."),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}),
        error_messages={'required': _("Make sure to provide a last name.")}
    )

    middle_initial = forms.CharField(
        label=_("What is your middle initial?"), 
        empty_value=(""),
        max_length=5,
        required=False
    )

    rent_or_own = forms.ChoiceField(
        label=_("Do you rent or own your home?"),
        choices=(
            ('rent',_("Rent")),
            ('own',_("Own")),
        ), 
        required=True,
        error_messages={'required': _("Make sure to indicate whether you own or rent.")}
    )

    account_holder = forms.ChoiceField(
        label=_("Who is responsible for paying the water bill?"),
        help_text=_("This is the name of the account holder listed on your water bill"),
        required=True,
        choices=ACCOUNT_HOLDER_CHOICES,
        error_messages={'required': _("Make sure to indicate who officially pays the water bill.")}
    )


class AddressForm(forms.Form):
    street_address = forms.CharField(
        label=_("What is your street address?"), 
        max_length=200, 
        validators=[RegexValidator(
            regex=r'^\d+ .*', 
            message=_("Make sure to enter a street number before the street name, for example 123 Main St")
        )],
        widget=forms.TextInput(attrs={'placeholder': "123 Main St"},),
        error_messages={'required': _("Make sure to provide a street address.")}
    )

    apartment_unit = forms.CharField(
        label=_("If this is an apartment, what is the apartment unit?"), 
        help_text=_("Skip this if you don't live in an apartment"),
        required=False,
        max_length=10
    )

    zip_code = forms.CharField(
        label=_("What is your 5 digit ZIP code?"), 
        validators=[RegexValidator(
            regex=r'^\d{5}$', 
            message=_("Your ZIP code must be exactly 5 digits")
        )],
        error_messages={'required': _("Make sure to provide a 5 digit ZIP code.")}
    )

    card_title = _("Where are you currently living?")


class ContactInfoForm(forms.Form):
    phone_number = forms.CharField(
        max_length=17, 
        widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}),
        error_messages={'required': _("Make sure to provide a valid phone number.")}
    )

    email_address = forms.EmailField(
        label=_("What is your email address?"), 
        help_text=_("Please provide if you wish to receive status updates on your application."), 
        required=False
    )

    card_title = _("Okay, let's get your contact info.")

    def clean_phone_number(self):
        return cleanPhoneNumberFormat(self)


class AccountHolderForm(forms.Form):
    account_first = forms.CharField(
        label=_("What is the account holder's first name?"), 
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': _("First name")}),
        error_messages={'required': _("Make sure to provide a first name.")}
    )

    account_last = forms.CharField(
        label=_("What is the account holder's last name?"), 
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}),
        error_messages={'required': _("Make sure to provide a last name.")}
    )

    account_middle = forms.CharField(
        label=_("What is the account holder's middle initial?"), 
        max_length=5, 
        required=False, 
        empty_value=("")
    )

    card_title = _("Whose name is officially on your water bill?")


class AccountNumberForm(forms.Form):
    account_number = forms.CharField(
        label=_("What is your water account number?"), 
        help_text=_("Your Buffalo Water account number can be found on your bill"), 
        required=False
    )

    has_account_number = forms.BooleanField(
        required=False, 
        widget=forms.HiddenInput()
    )

    card_title = _("Almost done! Let's get info on your water account.")


class LegalForm(forms.Form):
    legal_agreement = forms.BooleanField(
        label=_("I agree"),
        required=True, 
        widget=widgets.CheckboxInput,  
        error_messages={'required': _("You must agree to the terms to continue")}
    )

class ReferralForm(ModelForm):
    class Meta:
        model = Referral
        fields = ['facebook', 'google', 'twitter', 'linkedin', 'bill', 'ad', 
                  'pamphlet', 'word_of_mouth', 'custom_referral']

    choices = [
        ('facebook', _('Facebook')),
        ('google', _('Google')),
        ('twitter', _('Twitter')),
        ('linkedin', _('LinkedIn')),
        ('bill', _('Letter inserted in water bill')),
        ('ad', _('Advertisement on bus, poster, or billboard')),
        ('pamphlet', _('Pamphlet')),
        ('word_of_mouth', _('Word of Mouth'))
    ]

    custom_referral = forms.CharField(
        label=_("Please type if you learned about the program another way"),
        help_text=_("This question is not required, but your answers help us improve our service outreach."),
        required=False,
        strip=True
    )

class SignatureForm(forms.Form):
    signature = forms.CharField(
        label=_("Type your full legal name to sign this application"), 
        max_length=250, 
        required=True, 
        error_messages={'required':_("You must sign the application to continue.")}
    )

class DocumentForm(forms.Form):
    doc = forms.FileField(
        validators=[ACCEPTED_FILE_VALIDATOR], 
        required=False)

class LaterDocumentsForm(forms.Form):
    first_name = forms.CharField(
        label=_("What is your first name?"),
        help_text=_("Legally as it appears on your ID."),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _("First name")})
    )

    last_name = forms.CharField(
        label=_("What is your last name?"),
        help_text=_("Legally as it appears on your ID."),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _("Last name")})
    )

    middle_initial = forms.CharField(
        label=_("What is your middle initial?"),
        help_text=_("Optional"),
        max_length=5,
        required=False, 
        empty_value=("")
    )

    zip_code = forms.CharField(
        label=_("What is your 5 digit ZIP code?"),
        validators=[RegexValidator(
            regex=r'^\d{5}$', 
            message=_("Your ZIP code must be exactly 5 digits")
        )]
    )
    phone_number = forms.CharField(
        label=_("What is your phone number?"),
        max_length=17,
        widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}))

    email_address = forms.EmailField(
        label=_("What is your email address?"),
        help_text=_("Optional"),
        required=False)

    card_title = _("Before submitting your documents, we need to match your information to an existing application.")

class MoreDocumentInfoRequiredForm(forms.Form):
    HOUSEHOLD_SIZE_CHOICES = getIntTuplesInclusive(1, 8, True)

    rent_or_own = forms.ChoiceField(
        label=_("Do you rent or own your home?"),
        required=True,
        choices=(('rent',_("Rent")),('own',_("Own")))
    )

    apartment_unit = forms.CharField(
        label=_("If this is an apartment, what is the apartment unit?"), 
        help_text=_("Skip this if you don't live in an apartment"),
        required=False, 
        max_length=10
    )

    street_address = forms.CharField(
        label=_("What is your street address?"), 
        max_length=200, 
        widget=forms.TextInput(attrs={'placeholder': "123 Main St"}),
        validators=[RegexValidator(
            regex=r'^\d+ .*',
            message=_("Make sure to enter a street number before the street name, for example 123 Main St"))
        ]
    )

    household_size = forms.ChoiceField(
        label=_("What is your household size?"),
        help_text=_("Typically how many people you regularly share living expenses with, including yourself. "
                    "If you live with them, include children under 21, spouses/partners, and parents."),
        required=True,
        choices=HOUSEHOLD_SIZE_CHOICES
    )

    card_title = _("We need more information to find your existing application.")

class ForgiveReviewApplicationForm(forms.Form):
    submit_application = forms.ChoiceField(
        label=_("Would you like to submit this application?"),
        choices=((True,_('Yes')), (False,_('No')))
    )

class ForgiveResidentInfoForm(forms.Form):
    card_title = _("Let's get some basic information.")

    first_name = forms.CharField(
        label=_("What is your first name?"), 
        help_text=_("Legally as it appears on your ID."),
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': _("First name")}),
        error_messages={'required': _("Make sure to provide a first name.")}
    )

    last_name = forms.CharField(
        label=_("What is your last name?"), 
        help_text=_("Legally as it appears on your ID."),
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': _("Last name")}),
        error_messages={'required': _("Make sure to provide a last name.")}
    )

    middle_initial = forms.CharField(
        label=_("What is your middle initial?"),
        help_text=_("Not required"),
        max_length=5, 
        required=False, 
        empty_value=("")
    )

    street_address = forms.CharField(
        label=_("What is your street address?"), 
        max_length=200, 
        validators=[RegexValidator(
            regex=r'^\d+ .*', 
            message=_("Make sure to enter a street number before the street name, for example 123 Main St"))], 
        widget=forms.TextInput(attrs={'placeholder': "123 Main St"}),
        error_messages={'required': _("Make sure to provide a street address.")}
    )

    apartment_unit = forms.CharField(
        label=_("If this is an apartment, what is the apartment unit?"), 
        help_text=_("Skip this if you don't live in an apartment"),
        required=False, 
        max_length=10)

    zip_code = forms.CharField(
        label=_("What is your 5 digit ZIP code?"), 
        validators=[RegexValidator(
            regex=r'^\d{5}$',
            message=_("Your ZIP code must be exactly 5 digits")
        )],
        error_messages={'required': _("Make sure to provide a 5 digit ZIP code.")}
    )

    phone_number = forms.CharField(
        label=_("What is your phone number?"),
        max_length=17, 
        widget=forms.TextInput(attrs={'placeholder': _("716-555-5555")}),
        error_messages={'required': _("Make sure to provide a valid phone number.")}
    )

    email_address = forms.EmailField(
        label=_("What is your email address?"),
        help_text=_("Not required"),
        required=False
    )

    def clean_phone_number(self):
        return cleanPhoneNumberFormat(self)
