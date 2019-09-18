from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import (
    ApplicationForm, DocumentForm, AccountForm, HouseholdForm, AutoEligibleForm,
     ExactIncomeForm, HourlyIncomeForm, EstimateIncomeForm)
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .models import Application
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

# Step 1
class HouseholdView(FormView):
    template_name = 'pathways/apply.html'
    form_class = HouseholdForm
    success_url = '/apply/household-eligible/'

    def form_valid(self, form):
        self.request.session['household'] = form.cleaned_data['household']
        return super().form_valid(form)

# Step 2
class AutoEligibleView(FormView):
    template_name = 'pathways/apply-household-benefits.html'
    form_class = AutoEligibleForm
    success_url = '/apply/income-methods/'

    def form_valid(self, form):
        hasHouseholdBenefits = form.cleaned_data['hasHouseholdBenefits']
        self.request.session['hasHouseholdBenefits'] = form.cleaned_data['hasHouseholdBenefits']
        return super().form_valid(form)

# TODO: Refactor IncomeViews into single view with conditional for which method was selected
# Step 3
class IncomeMethodsView(TemplateView):
    template_name = 'pathways/apply-income-methods.html'

# Step 4 (exact)
class ExactIncomeView(FormView):
    template_name = 'pathways/apply-exact-income.html'
    form_class = ExactIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        return super().form_valid(form)

# Step 4 (hourly)
class HourlyIncomeView(FormView):
    template_name = 'pathways/apply-hourly-income.html'
    form_class = HourlyIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
        return super().form_valid(form)

# Step 4 (estimate)
class EstimateIncomeView(FormView):
    template_name = 'pathways/apply-estimate-income.html'
    form_class = EstimateIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self,form)
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
    locale.setlocale( locale.LC_ALL, '' )
    return locale.currency(annual_income, grouping=True)
# End Income Helpers

# Step 5
class ReviewEligibilityView(TemplateView):
    template_name = 'pathways/apply-review-eligibility.html'



def eligibleView(request):
    if isEligibleHelper(request.session):
        return render(request, 'pathways/apply-qualify.html')
    
def isEligibleHelper(session):
    """Returns boolean of whether applicant is eligible based on session info """
    return True

# https://www.reddit.com/r/django/comments/ad7ulo/when_and_how_to_use_django_formview/edg21b6/

# class ApplicationView(FormView):
#     template_name = 'pathways/apply.html'
#     form_class = ApplicationForm
#     success_url = '/apply-account/'

#     def form_valid(self, form):
#         application = form.save()
#         app_id = application.id
#         self.request.session['app_id'] = app_id
#         return super().form_valid(form)

# class DocumentView(FormView):
#     template_name = 'pathways/apply.html'
#     form_class = AccountForm
#     success_url = ''

#     def form_valid(self, form):
#         documents = form.save(commit=False)
#         if self.request.session['app_id']:
#             documents.application = self.request.session['app_id'] = app_id 
#         return super().form_valid(form)

# class AccountView(FormView):
#     template_name = 'pathways/apply.html'
#     form_class = AccountForm
#     success_url = '/'

#     def get_form_kwargs(self):
#         kwargs = super(AccountView, self).get_form_kwargs()
#         kwargs['app_id'] = self.request.session.get('app_id', None)
#         return kwargs

#     def form_valid(self, form):
#         account = form.save(commit=False)
#         account.application = Application.objects.filter(id=form.app_id)[0]
#         account = form.save()
#         messages.info(self.request, f'Account submit {account.application.id} ({account.application.phone_number})')
#         return super().form_valid(form)

# def account(request):
#     context = {}
#     app_id = request.session.get('app_id', None)
#     form = AccountForm(request.POST or None, app_id=app_id)
#     messages.info(request, f'App id is {app_id}')
#     if request.method == 'POST':
#             if form.is_valid():
#                 account = form.save(commit=False)
#                 account.application = Application.objects.filter(id=form.app_id)[0]
#                 messages.info(request, f'Account submit {account.application.id} ({account.application.phone_number})')
#                 return redirect('/')
#     else:
#         context['form'] = form
#         return render(request, 'pathways/apply-account.html', context)

# def apply(request):
#     context = {}
#     initial = {'app_id': request.session.get('app_id', None)}
#     form = ApplicationForm(request.POST or None, initial=initial)
#     if request.method == 'POST':
#         if form.is_valid():
#             application = form.save()
#             app_id = application.id
#             request.session['app_id'] = app_id
#             messages.info(request, f'Test submit {app_id}')
#             return redirect('/apply-account')
#     else:
#         form = ApplicationForm()
#     context['form'] = form
#     return render(request, 'pathways/apply.html', context)