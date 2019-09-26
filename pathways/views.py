from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from . import forms
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .models import Application, Income
import locale

# Create your views here.
def home(request):
    context = {}
    return render(request, 'pathways/home.html', context)

def about(request):
    return render(request, 'pathways/about.html', {'title':'About'})

def debugsessionview(request):
    context = {}
    return render(request, 'pathways/debug-session.html', context)

# Considerations between Class-Based Views and Function-Based Views
# https://www.reddit.com/r/django/comments/ad7ulo/when_and_how_to_use_django_formview/edg21b6/

# Step 1
class HouseholdView(FormView):
    template_name = 'pathways/apply.html'
    form_class = forms.HouseholdForm
    success_url = '/apply/household-eligible/'

    def form_valid(self, form):
        self.request.session['household'] = form.cleaned_data['household']
        self.request.session['active_app'] = True
        return super().form_valid(form)

# Step 2
class AutoEligibleView(FormView):
    template_name = 'pathways/apply-household-benefits.html'
    form_class = forms.AutoEligibleForm
    success_url = '/apply/income-methods/'

    def form_valid(self, form):
        hasHouseholdBenefits = form.cleaned_data['hasHouseholdBenefits']
        self.request.session['hasHouseholdBenefits'] = form.cleaned_data['hasHouseholdBenefits']
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(AutoEligibleView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# TODO: Refactor IncomeViews into single view with conditional for which method was selected, using ContextMixins
# Step 3
class IncomeMethodsView(TemplateView):
    template_name = 'pathways/apply-income-methods.html'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(IncomeMethodsView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# Step 4 (exact)
class ExactIncomeView(FormView):
    template_name = 'pathways/apply-exact-income.html'
    form_class = forms.ExactIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(ExactIncomeView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# Step 4 (hourly)
class HourlyIncomeView(FormView):
    template_name = 'pathways/apply-hourly-income.html'
    form_class = forms.HourlyIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(HourlyIncomeView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# Step 4 (estimate)
class EstimateIncomeView(FormView):
    template_name = 'pathways/apply-estimate-income.html'
    form_class = forms.EstimateIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(EstimateIncomeView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

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
class ReviewEligibilityView(TemplateView):
    template_name = 'pathways/apply-review-eligibility.html'

    # https://stackoverflow.com/questions/5433172/how-to-redirect-on-conditions-with-class-based-views-in-django-1-3/12021673
    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(ReviewEligibilityView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apply_step'] = 'review-eligibility'
        locale.setlocale( locale.LC_ALL, '' )
        context['income_formatted'] = locale.currency(self.request.session['annual_income'], grouping=True)
        return context

# Step 6
class EligibilityView(TemplateView):
    template_name = 'pathways/apply-eligibility.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['isEligible'] = int(self.request.session['annual_income']) <= incomeLimits[int(self.request.session['household'])]
        locale.setlocale( locale.LC_ALL, '' )
        context['income_formatted'] = locale.currency(
            self.request.session['annual_income'], grouping=True)
        context['income_limit'] = locale.currency(
            incomeLimits[int(self.request.session['household'])], grouping=True)
        return context

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(EligibilityView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

incomeLimits = {
    1: 41850,
    2: 47800,
    3: 53800,
    4: 59750,
    5: 64550,
    6: 69350,
    7: 74100,
    8: 78900,
}

# Step 7
class AdditionalQuestionsView(TemplateView):
    template_name = 'pathways/apply-additional-questions.html'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(AdditionalQuestionsView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# Step 8
class ResidentInfoView(FormView):
    template_name = 'pathways/apply.html'
    form_class = forms.ResidentInfoForm
    success_url = '/apply/address/'

    def form_valid(self, form):
        self.request.session['first_name'] = form.cleaned_data['first_name']
        self.request.session['last_name'] = form.cleaned_data['last_name']
        self.request.session['middle_initial'] = form.cleaned_data['middle_initial']
        self.request.session['rent_or_own'] = form.cleaned_data['rent_or_own']
        self.request.session['account_holder'] = form.cleaned_data['account_holder']
        #  Redirects to fill in account holder info
        if self.request.session['account_holder'] in ['landlord', 'other']:
            self.success_url = '/apply/account-holder/'
        else:
            self.request.session['account_first'] = form.cleaned_data['first_name']
            self.request.session['account_last'] = form.cleaned_data['last_name']
            self.request.session['account_middle'] = form.cleaned_data['middle_initial']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(ResidentInfoView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

# Step 9
class AccountHolderView(FormView):
    template_name = 'pathways/apply.html'
    form_class = forms.AccountHolderForm
    success_url = '/apply/address/'

    def form_valid(self, form):
        self.request.session['account_first'] = form.cleaned_data['account_first']
        self.request.session['account_last'] = form.cleaned_data['account_last']
        self.request.session['account_middle'] = form.cleaned_data['account_middle']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(AccountHolderView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

class AddressView(FormView):
    template_name = 'pathways/apply.html'
    form_class = forms.AddressForm
    success_url = '/apply/contact-info/'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(AddressView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

    def form_valid(self, form):
        self.request.session['street_address'] = form.cleaned_data['street_address']
        self.request.session['apartment_unit'] = form.cleaned_data['apartment_unit']
        self.request.session['zip_code'] = form.cleaned_data['zip_code']
        return super().form_valid(form)

class ContactInfoView(FormView):
    template_name = 'pathways/apply.html'
    form_class = forms.ContactInfoForm
    success_url = '/apply/account-number/'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(ContactInfoView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

    def form_valid(self, form):
        self.request.session['phone_number'] = form.cleaned_data['phone_number']
        self.request.session['email_address'] = form.cleaned_data['email_address']
        return super().form_valid(form)
        
class AccountNumberView(FormView):
    template_name = 'pathways/apply-account-number.html'
    form_class = forms.AccountNumberForm
    success_url = '/apply/review-application/'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(AccountNumberView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

    def form_valid(self, form):
        self.request.session['account_number'] = form.cleaned_data['account_number']
        return super().form_valid(form)

class ReviewApplicationView(TemplateView):
    template_name = 'pathways/apply-review-application.html'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(ReviewApplicationView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale.setlocale( locale.LC_ALL, '' )
        context['income_formatted'] = locale.currency(self.request.session['annual_income'], grouping=True)
        return context

class LegalView(FormView):
    template_name = 'pathways/apply-legal.html'
    form_class = forms.LegalForm
    success_url = '/apply/signature/'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(LegalView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')
    
    def form_valid(self, form):
        self.request.session['legal_agreement'] = form.cleaned_data['legal_agreement']
        return super().form_valid(form)

class SignatureView(FormView):
    template_name = 'pathways/apply-signature.html'
    form_class = forms.SignatureForm
    success_url = '/debug/'

    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(SignatureView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

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
        app.household_size = self.request.session['household']
        app.hasHouseholdBenefits = self.request.session['hasHouseholdBenefits']

        # Legal and Signature Info
        app.legal_agreement = self.request.session['legal_agreement']
        app.signature = self.request.session['signature']

        app.save()

        if self.request.session['hasHouseholdBenefits'] == 'False':
            income = Income(application = app)
            income.annual_income = self.request.session['annual_income']
            income.save()
        return super().form_valid(form)