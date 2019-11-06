from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from . import forms
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .models import Application
import locale
import datetime

class ExtraContextView(TemplateView):
    extra_context = {}
    def get_context_data(self, *args, **kwargs):
        context = super(ExtraContextView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context

class DispatchView(ExtraContextView):
    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(DispatchView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')
    

# Create your views here.
class HomeView(ExtraContextView):
    template_name = 'pathways/home.html'
    extra_context = {'isHomepage': True}

class AboutView(ExtraContextView):
    template_name = 'pathways/about.html'
    extra_context = {'title':'About'}

# Considerations between Class-Based Views and Function-Based Views
# https://www.reddit.com/r/django/comments/ad7ulo/when_and_how_to_use_django_formview/edg21b6/

class ApplyView(TemplateView):
    template_name = 'pathways/apply/overview.html'

    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        return super(ApplyView, self).dispatch(request, *args, **kwargs)

class HouseholdView(FormView):
    template_name = 'pathways/apply/household-size.html'
    form_class = forms.HouseholdForm
    success_url = reverse_lazy('pathways-apply-household-benefits')

    def form_valid(self, form):
        self.request.session['household_size'] = form.cleaned_data['household_size']
        self.request.session['active_app'] = True
        return super().form_valid(form)

# Step 2
class HouseholdBenefitsView(FormView, DispatchView):
    template_name = 'pathways/apply/household-benefits.html'
    form_class = forms.HouseholdBenefitsForm
    success_url = reverse_lazy('pathways-apply-income-methods')

    def form_valid(self, form):
        hasHouseholdBenefits = form.cleaned_data['hasHouseholdBenefits']
        self.request.session['hasHouseholdBenefits'] = form.cleaned_data['hasHouseholdBenefits']
        if hasHouseholdBenefits == 'True':
            self.success_url = reverse_lazy('pathways-apply-eligibility')
        return super().form_valid(form)


# TODO: Refactor IncomeViews into single view with conditional for which method was selected, using ContextMixins
# Step 3
class IncomeMethodsView(DispatchView):
    template_name = 'pathways/apply/income-methods.html'

# Step 4 (exact)
class ExactIncomeView(FormView, DispatchView):
    template_name = 'pathways/apply/exact-income.html'
    form_class = forms.ExactIncomeForm
    success_url = reverse_lazy('pathways-apply-review-eligibility')

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        self.request.session['income_method'] = 'exact'
        return super().form_valid(form)

# Step 4 (hourly)
class HourlyIncomeView(FormView, DispatchView):
    template_name = 'pathways/apply/hourly-income.html'
    form_class = forms.HourlyIncomeForm
    success_url = reverse_lazy('pathways-apply-review-eligibility')

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        self.request.session['income_method'] = 'hourly'
        return super().form_valid(form)

# Step 4 (estimate)
class EstimateIncomeView(FormView, DispatchView):
    template_name = 'pathways/apply/estimate-income.html'
    form_class = forms.EstimateIncomeForm
    success_url = reverse_lazy('pathways-apply-review-eligibility')

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        self.request.session['income_method'] = 'estimate'
        return super().form_valid(form)

# Income Helpers
def processIncomeHelper(general_income_view, form):
    """Returns modified session after calculating annual income from form"""
    income = form.cleaned_data['income']
    pay_period = form.cleaned_data['pay_period']
    annual_income = calculateIncomeHelper(income, pay_period)
    general_income_view.request.session['annual_income'] = annual_income
    general_income_view.request.session['income'] = income
    general_income_view.request.session['pay_period'] = pay_period
    return general_income_view.request.session

def calculateIncomeHelper(income, pay_period):
    """Returns annual income based on income each pay_period"""
    if pay_period == 'weekly':
        annual_income = income*50
    elif pay_period == 'biweekly':
        annual_income = income*25
    elif pay_period == 'semimonthly':
        annual_income = income*24
    elif pay_period == 'monthly':
        annual_income = income*12
    else:
        annual_income = income*pay_period*50 #Hourly
    return annual_income
# End Income Helpers

# Step 5
class ReviewEligibilityView(DispatchView):
    template_name = 'pathways/apply/review-eligibility.html'

    def __init__(self, *args, **kwargs):
        super(ReviewEligibilityView, self).__init__(*args, **kwargs)
        self.extra_context['apply_step'] = 'review-eligibility'
        locale.setlocale( locale.LC_ALL, '' )
        self.extra_context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])
        self.extra_context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
        self.extra_context['pay_period'] = self.request.session['pay_period']
        self.extra_context['income_method'] = self.request.session['income_method']

# Step 6
class EligibilityView(DispatchView):
    template_name = 'pathways/apply/eligibility.html'
    incomeLimits = {1: 41850, 2: 47800, 3: 53800, 4: 59750, 5: 64550, 6: 69350, 7: 74100, 8: 78900,}

    def __init__(self, *args, **kwargs):
        super(EligibilityView, self).__init__(*args, **kwargs)
        if self.request.session['hasHouseholdBenefits'] == 'True':
            self.extra_context['isEligible'] = True
        else:
            self.extra_context['isEligible'] = int(self.request.session['annual_income']) <= incomeLimits[int(self.request.session['household_size'])]
        locale.setlocale( locale.LC_ALL, '' )
        self.extra_context['income_formatted'] = locale.currency(self.request.session['annual_income'], grouping=True)
        self.extra_context['income_limit'] = locale.currency(incomeLimits[int(self.request.session['household_size'])], grouping=True)

# Step 7
class AdditionalQuestionsView(DispatchView):
    template_name = 'pathways/apply/additional-questions.html'

# Step 8
class ResidentInfoView(FormView, DispatchView):
    template_name = 'pathways/apply/resident-info.html'
    form_class = forms.ResidentInfoForm
    success_url = reverse_lazy('pathways-apply-address')

    def form_valid(self, form):
        for field in ['first_name', 'last_name', 'middle_initial', 'rent_or_own', 'account_holder']:
            self.request.session[field] = form.cleaned_data[field]
        #  Redirects to fill in account holder info
        if self.request.session['account_holder'] in ['landlord', 'other']:
            self.success_url = reverse_lazy('pathways-apply-account-holder')
        else:
            for field in ['account_first', 'account_last', 'account_middle']:
                self.request.session[field] = form.cleaned_data[field]
        return super().form_valid(form)

# Step 9
class AccountHolderView(FormView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AccountHolderForm
    success_url = reverse_lazy('pathways-apply-address')
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        for field in ['account_first', 'account_last', 'account_middle']:
                self.request.session[field] = form.cleaned_data[field]
        return super().form_valid(form)

class AddressView(FormView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AddressForm
    success_url = reverse_lazy('pathways-apply-contact-info')
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        self.request.session['street_address'] = form.cleaned_data['street_address']
        self.request.session['apartment_unit'] = form.cleaned_data['apartment_unit']
        self.request.session['zip_code'] = form.cleaned_data['zip_code']
        return super().form_valid(form)


class ContactInfoView(FormView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.ContactInfoForm
    success_url = reverse_lazy('pathways-apply-account-number')
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        self.request.session['phone_number'] = form.cleaned_data['phone_number']
        self.request.session['email_address'] = form.cleaned_data['email_address']
        return super().form_valid(form)

        
class AccountNumberView(FormView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AccountNumberForm
    success_url = reverse_lazy('pathways-apply-review-application')
    extra_context = {'card_title': form_class.card_title, 'isAccountNumberView':True}

    def form_valid(self, form):
        self.request.session['account_number'] = form.cleaned_data['account_number']
        self.request.session['hasAccountNumber'] = form.cleaned_data['hasAccountNumber']
        return super().form_valid(form)

class ReviewApplicationView(DispatchView):
    template_name = 'pathways/apply/review-application.html'
    
    def __init__(self, *args, **kwargs):
        super(ReviewApplicationView, self).__init__(*args, **kwargs)
        if self.request.session['hasHouseholdBenefits'] == 'True':
            self.extra_context['isEligible'] = True
        locale.setlocale( locale.LC_ALL, '' )
        self.context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])
        self.context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
        self.context['pay_period'] = self.request.session['pay_period']
        self.context['income_method'] = self.request.session['income_method']

class LegalView(FormView):
    template_name = 'pathways/apply/legal.html'
    form_class = forms.LegalForm
    success_url = reverse_lazy('pathways-apply-signature')
    
    def form_valid(self, form):
        self.request.session['legal_agreement'] = form.cleaned_data['legal_agreement']
        return super().form_valid(form)

class SignatureView(FormView):
    template_name = 'pathways/apply/signature.html'
    form_class = forms.SignatureForm
    success_url = reverse_lazy('pathways-apply-documents-overview')

    def form_valid(self, form):
        self.request.session['signature'] = form.cleaned_data['signature']

        app = Application()
        
        # Personal Info
        app.first_name = self.request.session['first_name']
        app.last_name = self.request.session['last_name']
        app.middle_initial = self.request.session['middle_initial']
        app.rent_or_own = self.request.session['rent_or_own']

        app.street_address = self.request.session['street_address']
        app.apartment_unit = self.request.session['apartment_unit']
        app.zip_code = self.request.session['zip_code']

        app.phone_number = self.request.session['phone_number']
        app.email_address = self.request.session['email_address']

        # Billing Info
        app.account_holder = self.request.session['account_holder']
        app.account_first = self.request.session['account_first']
        app.account_last = self.request.session['account_last']
        app.account_middle = self.request.session['account_middle']
        app.account_number = self.request.session['account_number']

        # Eligibility Info
        app.household_size = self.request.session['household_size']
        app.hasHouseholdBenefits = self.request.session['hasHouseholdBenefits']
        if self.request.session['hasHouseholdBenefits'] == 'False':
            app.annual_income = self.request.session['annual_income']

        # Legal and Signature Info
        app.legal_agreement = self.request.session['legal_agreement']
        app.signature = self.request.session['signature']

        if self.request.session['hasHouseholdBenefits'] == 'False':
            app.annual_income = self.request.session['annual_income']

        app.save()
        self.request.session['app_id'] = app.id

        return super().form_valid(form)

class DocumentOverviewView(TemplateView):
    template_name = 'pathways/docs/overview.html'

    def __init__(self, *args, **kwargs):
        super(DocumentOverviewView, self).__init__(*args, **kwargs)
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        extra_context['hasHouseholdBenefits'] = app.hasHouseholdBenefits
        extra_context['rent_or_own'] = app.rent_or_own

class DocumentIncomeView(FormView, DispatchView):
    template_name = 'pathways/docs/upload-form.html'
    form_class = forms.DocumentIncomeForm
    success_url = reverse_lazy('pathways-apply-documents-residence')
    extra_context = {'next_url': reverse_lazy('pathways-apply-documents-residence')}

    def __init__(self, *args, **kwargs):
        super(DocumentIncomeView, self).__init__(*args, **kwargs)
        if self.request.session['hasHouseholdBenefits'] == 'True':
            self.form_class = forms.DocumentBenefitsForm
        else:
            self.form_class = forms.DocumentIncomeForm

    def form_valid(self, form):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        if self.request.session['hasHouseholdBenefits'] == 'True':
            app.benefits_photo = form.cleaned_data['benefits_photo']
        else:
            app.income_photo = form.cleaned_data['income_photo']
        app.save()
        return super().form_valid(form)

class DocumentResidenceView(FormView):
    template_name = 'pathways/docs/upload-form.html'
    success_url = reverse_lazy('pathways-apply-confirmation')
    extra_context = {'next_url': reverse_lazy('pathways-apply-documents-residence')}

    def __init__(self, *args, **kwargs):
        super(DocumentResidenceView, self).__init__(*args, **kwargs)
        if self.request.session['rent_or_own'] == 'rent':
            self.form_class = forms.DocumentTenantForm
        else:
            self.form_class = forms.DocumentHomeownerForm

    def form_valid(self, form):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        app.residence_photo = form.cleaned_data['residence_photo']
        app.save()
        return super().form_valid(form)        

class ConfirmationView(TemplateView):
    template_name = 'pathways/apply/confirmation.html'

    def __init__(self, *args, **kwargs):
        super(ConfirmationView, self).__init__(*args, **kwargs)
        extra_context['confirm_timestamp'] = datetime.datetime.now().strftime("%m/%d/%Y")
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        extra_context['hasHouseholdBenefits'] = app.hasHouseholdBenefits
        extra_context['has_income_photo'] = app.income_photo not None
        extra_context['has_benefits_photo'] = app.benefits_photo not None
        extra_context['has_residence_photo'] = app.benefits_photo not None