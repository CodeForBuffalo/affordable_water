from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
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

class FormToSessionView(FormView):
    def form_valid(self, form):
        for field in form:
            self.request.session[field.name] = form.cleaned_data[field.name]
        return super().form_valid(form)

class FormToAppView(FormView):
    def form_valid(self, form):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        for field in form:
            setattr(app, field.name, form.cleaned_data[field.name])
        app.save()
        return super().form_valid(form)

class ClearSessionView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        return super(ClearSessionView, self).dispatch(request, *args, **kwargs)
    

class DispatchView(ExtraContextView):
    def dispatch(self, request, *args, **kwargs):
        if 'active_app' in request.session:
            return super(DispatchView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

class FormToSessionView(FormView):
    def form_valid(self, form):
        for field in form:
            self.request.session[field.name] = form.cleaned_data[field.name]
        return super().form_valid(form)

class FormToAppView(FormView):
    def form_valid(self, form):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        for field in form:
            setattr(app, field.name, form.cleaned_data[field.name])
        app.save()
        return super().form_valid(form)      
    

# Create your views here.
class HomeView(ExtraContextView):
    template_name = 'pathways/home.html'
    extra_context = {'isHomepage': True}

class AboutView(ExtraContextView):
    template_name = 'pathways/about.html'
    extra_context = {'title':'About'}

# Considerations between Class-Based Views and Function-Based Views
# https://www.reddit.com/r/django/comments/ad7ulo/when_and_how_to_use_django_formview/edg21b6/

class ApplyView(ExtraContextView):
    template_name = 'pathways/apply/overview.html'

    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        return super(ApplyView, self).dispatch(request, *args, **kwargs)

class HouseholdSizeView(FormToSessionView):
    template_name = 'pathways/apply/household-size.html'
    form_class = forms.HouseholdSizeForm
    success_url = '/apply/household-benefits/'

    def form_valid(self, form):
        self.request.session['active_app'] = True
        return super().form_valid(form)

# Step 2
class HouseholdBenefitsView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/household-benefits.html'
    form_class = forms.HouseholdBenefitsForm
    success_url = '/apply/household-contributors/'

    def form_valid(self, form):
        if (form.cleaned_data['hasHouseholdBenefits'] == 'True'):
            self.success_url = '/apply/eligibility/'
        return super().form_valid(form)


class HouseholdContributorsView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/household-contributors.html'
    form_class = forms.HouseholdContributorsForm
    success_url = '/apply/income/'

    def form_valid(self, form):
        if (form.cleaned_data['household_contributors'] == '1'):
            self.success_url = '/apply/job-status/'
        else:
            self.request.session['income_method'] = 'estimate'
        return super().form_valid(form)

class JobStatusView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/job-status.html'
    form_class = forms.JobStatusForm
    success_url = '/apply/self-employment/'

class SelfEmploymentView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/self-employment.html'
    form_class = forms.SelfEmploymentForm
    success_url = '/apply/other-income-sources/'

class OtherIncomeSourcesView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/other-income-sources.html'
    form_class = forms.OtherIncomeSourcesForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        if (str(self.request.session['has_job']) == 'True' or str(self.request.session['is_self_employed']) == 'True'):
            self.success_url = '/apply/number-of-jobs/'
        elif (str(form.cleaned_data['has_other_income']) == 'True'):
            self.success_url = '/apply/non-job-income/'
        else:
            self.success_url = '/apply/review-eligibility/'
        return super().form_valid(form)

class NumberOfJobsView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/number-of-jobs.html'
    form_class = forms.NumberOfJobsForm
    success_url = '/apply/income/'

    def form_valid(self, form):
        if (int(form.cleaned_data['number_of_jobs']) == 1):
            self.success_url = '/apply/income-methods/'
        else:
            self.request.session['income_method'] = 'estimate'
        return super().form_valid(form)

class NonJobIncomeView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/non-job-income.html'
    form_class = forms.NonJobIncomeForm
    success_url = '/apply/review-eligibility'

class IncomeMethodsView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/income-methods.html'
    form_class = forms.IncomeMethodsForm
    success_url = '/apply/income/'

class IncomeView(FormToSessionView, DispatchView):
    success_url = '/apply/review-eligibility/'

    def get_form_class(self):
        if self.request.session['income_method'] == 'exact':
            self.form_class = forms.ExactIncomeForm
        elif self.request.session['income_method'] == 'hourly':
            self.form_class = forms.HourlyIncomeForm
        else:
            self.form_class = forms.EstimateIncomeForm
        return self.form_class

    def get_template_names(self):
        if self.request.session['income_method'] == 'exact':
            self.template_name = 'pathways/apply/exact-income.html'
        elif self.request.session['income_method'] == 'hourly':
            self.template_name = 'pathways/apply/hourly-income.html'
        else:
            self.template_name = 'pathways/apply/estimate-income.html'
        return super().get_template_names()

    def form_valid(self, form):
        self.request.session = processIncomeHelper(self.request.session,form)
        return super().form_valid(form) 

# Income Helpers
def processIncomeHelper(session, form):
    """Returns modified session after calculating annual income from form"""
    session['income'] = form.cleaned_data['income']
    session['pay_period'] = form.cleaned_data['pay_period']
    session['annual_income'] = calculateIncomeHelper(session['income'], session['pay_period'])
    return session

def calculateIncomeHelper(income, pay_period):
    """Returns annual income based on income each pay_period"""
    pay_multipliers = {'weekly':52, 'biweekly':25, 'semimonthly':24,'monthly':12}
    return income*pay_multipliers[pay_period] if pay_period in pay_multipliers else income*pay_period*52 #Hourly
# End Income Helpers

# Step 5
class ReviewEligibilityView(DispatchView):
    template_name = 'pathways/apply/review-eligibility.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if(str(self.request.session['has_job']) == 'False' 
            and str(self.request.session['is_self_employed']) == 'False' 
            and str(self.request.session['has_other_income']) == 'False'):
                context['no_income'] = True
                self.request.session['annual_income'] = 0
                self.request.session['income'] = 0
        if 'non_job_income' in self.request.session.keys():
            context['non_job_income_formatted'] = '${:,.0f}'.format(self.request.session['non_job_income'])
            self.request.session['annual_income'] = self.request.session['annual_income'] + self.request.session['non_job_income']
            if 'income' not in self.request.session.keys():
                self.request.session['income'] = 0
        context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])
        context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
        return context
        
# Step 6
class EligibilityView(DispatchView):
    template_name = 'pathways/apply/eligibility.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incomeLimits = {1: 41850, 2: 47800, 3: 53800, 4: 59750, 5: 64550, 6: 69350, 7: 74100, 8: 78900,}
        if self.request.session['hasHouseholdBenefits'] == 'True':
            context['isEligible'] = True
        else:
            context['isEligible'] = int(self.request.session['annual_income']) <= incomeLimits[int(self.request.session['household_size'])]
            context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
            context['income_limit'] = '${:,.0f}'.format(incomeLimits[int(self.request.session['household_size'])])
        return context

# Step 7
class AdditionalQuestionsView(DispatchView):
    template_name = 'pathways/apply/additional-questions.html'

# Step 8
class ResidentInfoView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/resident-info.html'
    form_class = forms.ResidentInfoForm
    success_url = '/apply/address/'

    def form_valid(self, form):
        #  Redirects to fill in account holder info
        if form.cleaned_data['account_holder'] in ['landlord', 'other']:
            self.success_url = '/apply/account-holder/'
        else:
            self.request.session['account_first'] = form.cleaned_data['first_name']
            self.request.session['account_last'] = form.cleaned_data['last_name']
            self.request.session['account_middle'] = form.cleaned_data['middle_initial']
        return super().form_valid(form)

# Step 9
class AccountHolderView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AccountHolderForm
    success_url = '/apply/address/'
    extra_context = {'card_title': form_class.card_title}

class AddressView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AddressForm
    success_url = '/apply/contact-info/'
    extra_context = {'card_title': form_class.card_title}

class ContactInfoView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.ContactInfoForm
    success_url = '/apply/account-number/'
    extra_context = {'card_title': form_class.card_title}

class AccountNumberView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.AccountNumberForm
    success_url = '/apply/review-application/'
    extra_context = {'card_title': form_class.card_title, 'isAccountNumberView':True}

class ReviewApplicationView(DispatchView):
    template_name = 'pathways/apply/review-application.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale.setlocale( locale.LC_ALL, '' )
        context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])
        context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
        return context

class LegalView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/legal.html'
    form_class = forms.LegalForm
    success_url = '/apply/signature/'

class SignatureView(FormView, DispatchView):
    template_name = 'pathways/apply/signature.html'
    form_class = forms.SignatureForm
    success_url = '/apply/documents-overview/'

    def form_valid(self, form):
        self.request.session['signature'] = form.cleaned_data['signature']
        # Create new application, load data from session, and save
        app = Application()
        for field in Application._meta.get_fields():
            if field.name in ['id', 'income_photo','benefits_photo','residence_photo']:
                continue
            if field.name == 'annual_income' and self.request.session['hasHouseholdBenefits'] == True:
                continue
            if field.name == 'apartment_unit' and ('apartment_unit' not in self.request.session or self.request.session['apartment_unit'] == ''):
                continue
            if field.name == 'account_number' and self.request.session['hasAccountNumber'] == False:
                continue
            setattr(app, field.name, self.request.session[field.name])

        app.save()
        self.request.session['app_id'] = app.id
        return super().form_valid(form)

class DocumentOverviewView(DispatchView):
    template_name = 'pathways/docs/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        context['hasHouseholdBenefits'] = app.hasHouseholdBenefits
        context['rent_or_own'] = app.rent_or_own
        return context

class DocumentIncomeView(FormToAppView, DispatchView):
    template_name = 'pathways/docs/upload-form.html'
    form_class = forms.DocumentIncomeForm
    success_url = '/apply/documents-residence/'
    extra_context = {'next_url': success_url}

    def get_form_class(self):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        if str(app.hasHouseholdBenefits) == 'True':
            self.form_class = forms.DocumentBenefitsForm
        else:
            self.form_class = forms.DocumentIncomeForm
        return self.form_class

class DocumentResidenceView(FormToAppView, DispatchView):
    template_name = 'pathways/docs/upload-form.html'
    success_url = '/apply/confirmation/'
    extra_context = {'next_url': success_url}

    def get_form_class(self):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        if str(app.rent_or_own) == 'rent':
            self.form_class = forms.DocumentTenantForm
        else:
            self.form_class = forms.DocumentHomeownerForm
        return self.form_class

class ConfirmationView(DispatchView):
    template_name = 'pathways/apply/confirmation.html'
    extra_context = {'confirm_timestamp': datetime.datetime.now().strftime("%m/%d/%Y")}

class LaterDocumentsView(FormView, ClearSessionView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.LaterDocumentsForm
    success_url = '/apply/documents-overview/'
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        self.request.session['is_later_docs'] = True

        # Get list of possible application
        app_list = Application.objects.filter(
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                zip_code = form.cleaned_data['zip_code'],
                phone_number = form.cleaned_data['phone_number']
                )
                
        if form.cleaned_data['middle_initial'] != '':
            app_list = app_list(middle_initial = form.cleaned_data['middle_initial'])

        if form.cleaned_data['email_address'] != '':
            app_list = app_list(email_address = form.cleaned_data['email_address'])

        if len(app_list) == 0:
            # No matching application found
            self.success_url = '/apply/later-documents/no-match-found/'

        elif len(app_list) == 1:
            # Matching application successfully found
            app = app_list[0]
            self.request.session['app_id'] = app.id
            self.request.session['active_app'] = True

        else:
            self.request.session['first_name'] = form.cleaned_data['first_name']
            self.request.session['last_name'] = form.cleaned_data['last_name']
            self.request.session['middle_initial'] = form.cleaned_data['middle_initial']
            self.request.session['zip_code'] = form.cleaned_data['zip_code']
            self.request.session['phone_number'] = form.cleaned_data['phone_number']
            self.request.session['email_address'] = form.cleaned_data['email_address']

            # More information required to narrow down match
            self.success_url = '/apply/later-documents/more-info-needed/'
            pass

        return super().form_valid(form)

class NoDocumentFoundView(ExtraContextView):
    template_name = 'pathways/docs/no-doc-found.html'

class MoreDocumentInfoRequiredView(FormView):
    template_name = 'pathways/docs/more-doc-info.html'
    form_class = forms.MoreDocumentInfoRequiredForm
    success_url = '/apply/documents-overview/'
    extra_context = {'card_title': form_class.card_title}

    def dispatch(self, request, *args, **kwargs):
        if 'is_later_docs' in request.session:
            return super(MoreDocumentInfoRequiredView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

    def form_valid(self, form):
        # Get list of possible application
        app_list = Application.objects.filter(
                first_name = self.request.session['first_name'],
                last_name = self.request.session['last_name'],
                zip_code = self.request.session['zip_code'],
                phone_number = self.request.session['phone_number'],
                rent_or_own = form.cleaned_data['rent_or_own'],
                street_address = form.cleaned_data['street_address'],
                household_size = form.cleaned_data['household_size']
                )
        
        if form.cleaned_data['apartment_unit'] != '':
            app_list = app_list(apartment_unit = form.cleaned_data['apartment_unit'])

        if len(app_list) == 1:
            # Matching application successfully found
            app = app_list[0]
            self.request.session['app_id'] = app.id
            self.request.session['active_app'] = True
        else:
            # No matching application found
            self.success_url = '/apply/later-documents/no-match-found/'

        return super().form_valid(form)
