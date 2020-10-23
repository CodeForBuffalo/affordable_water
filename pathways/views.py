from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from . import forms
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .models import Application, Document, ForgivenessApplication, EmailCommunication, Referral
import locale
import datetime
from django.utils.translation import ugettext_lazy as _
from . import tasks
from django.core.exceptions import ObjectDoesNotExist
from . import helpers

def handler404(request, *args, **kwargs):
    response = render(request, 'pathways/404.html')
    response.status_code = 404
    return response

def handler500(request, *args, **kwargs):
    response = render(request, 'pathways/500.html')
    response.status_code = 500
    return response

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

class ClearSessionView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        return super(ClearSessionView, self).dispatch(request, *args, **kwargs)
    

# Create your views here.
class HomeView(ExtraContextView):
    template_name = 'pathways/home.html'
    extra_context = {'homepageHeaderTemplate': True}

class AboutView(ExtraContextView):
    template_name = 'pathways/about.html'
    extra_context = {'title':'About', 'aboutHeaderTemplate': True}

class NondiscriminationView(ExtraContextView):
    template_name = 'pathways/nondiscrimination.html'
    extra_context = {'title':'Nondiscrimination', 'aboutHeaderTemplate': True}

class PrivacyView(ExtraContextView):
    template_name = 'pathways/privacy.html'
    extra_context = {'title':'Privacy', 'aboutHeaderTemplate': True}

# Considerations between Class-Based Views and Function-Based Views
# https://www.reddit.com/r/django/comments/ad7ulo/when_and_how_to_use_django_formview/edg21b6/

class ApplyOverviewAssistanceView(ExtraContextView):
    template_name = 'pathways/apply/assistance-overview.html'

class ApplyDiscountView(ExtraContextView):
    template_name = 'pathways/apply/discount-overview.html'

    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        return super(ApplyDiscountView, self).dispatch(request, *args, **kwargs)

class CityResidentView(FormView):
    template_name = 'pathways/apply/city-resident.html'
    form_class = forms.CityResidentForm
    success_url = '/apply/household-size/'

    def form_valid(self, form):
        if (form.cleaned_data['city_resident'] == 'False'):
            self.success_url = '/apply/non-resident/'
        return super().form_valid(form)

class ForgiveOverviewView(ExtraContextView):
    template_name = 'pathways/forgive/water-amnesty.html'

    def dispatch(self, request, *args, **kwargs):
        for key in list(request.session.keys()):
            del request.session[key]
        request.session['forgive_step'] = 'overview'
        return super(ForgiveOverviewView, self).dispatch(request, *args, **kwargs)

class ForgiveCityResidentView(CityResidentView):
    success_url = '/forgive/additional-questions/'

    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        return super(ForgiveCityResidentView, self).dispatch(request, *args, **kwargs)

class ForgiveAdditionalQuestionsView(TemplateView):
    template_name = 'pathways/forgive/additional-questions.html'

    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        return super(ForgiveAdditionalQuestionsView, self).dispatch(request, *args, **kwargs)

class ForgiveResidentInfoView(FormToSessionView):
    template_name = 'pathways/apply/info-form.html'
    form_class = forms.ForgiveResidentInfoForm
    success_url = '/forgive/refer/'
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        self.request.session['forgive_step'] = 'filled_application'
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        return super(ForgiveResidentInfoView, self).dispatch(request, *args, **kwargs)

class ForgiveReferralView(FormView):
    template_name = 'pathways/referral.html'
    form_class = forms.ReferralForm
    success_url = '/forgive/review-application/'

    def form_valid(self, form):
        ref = Referral()
        ref.program = 'Amnesty'
        for value, text in form.choices:
            setattr(ref, value, form.cleaned_data[value])
        ref.custom_referral = form.cleaned_data['custom_referral']
        ref.save()
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        elif request.session['forgive_step'] not in ['filled_application', 'submit_application']:
            return redirect('pathways-forgive-resident-info')
        return super(ForgiveReferralView, self).dispatch(request, *args, **kwargs)

class ForgiveReviewApplicationView(FormView):
    template_name = 'pathways/forgive/review-application.html'
    form_class = forms.ForgiveReviewApplicationForm
    success_url = '/forgive/confirmation/'

    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        elif request.session['forgive_step'] not in ['filled_application', 'submit_application']:
            return redirect('pathways-forgive-resident-info')
        return super(ForgiveReviewApplicationView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get or create Forgiveness application, load data from session, and save
        app = None
        try:
            app = ForgivenessApplication.objects.get(
                first_name=self.request.session['first_name'],
                last_name=self.request.session['last_name'],
                street_address=self.request.session['street_address'],
                zip_code=self.request.session['zip_code'],
                phone_number=self.request.session['phone_number'],
            )
            for field in ForgivenessApplication._meta.get_fields():
                if field.name == 'email_address' and app.email_address != '':
                    continue
                if field.name in self.request.session:
                    setattr(app, field.name, self.request.session[field.name])
                    
        except ObjectDoesNotExist:
            app = ForgivenessApplication()
            for field in ForgivenessApplication._meta.get_fields():
                if field.name in self.request.session:
                    setattr(app, field.name, self.request.session[field.name])

        app.save()
        self.request.session['forgive_step'] = 'submit_application'
        return super().form_valid(form)

class ForgiveConfirmationView(ExtraContextView):
    template_name = 'pathways/forgive/confirmation.html'
    extra_context = {'confirm_timestamp': datetime.datetime.now().strftime("%m/%d/%Y")}

    def dispatch(self, request, *args, **kwargs):
        if 'forgive_step' not in request.session:
            return redirect('pathways-forgive-overview')
        elif request.session['forgive_step'] != 'submit_application':
            return redirect('pathways-forgive-resident-info')
        return super(ForgiveConfirmationView, self).dispatch(request, *args, **kwargs)

class NonResidentView(ExtraContextView):
    template_name = 'pathways/apply/non-resident.html'

class HouseholdSizeView(FormToSessionView):
    template_name = 'pathways/apply/household-size.html'
    form_class = forms.HouseholdSizeForm
    success_url = '/apply/household-benefits/'

    def form_valid(self, form):
        self.request.session['active_app'] = True
        return super().form_valid(form)


class HouseholdBenefitsView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/household-benefits.html'
    form_class = forms.HouseholdBenefitsForm
    success_url = '/apply/household-contributors/'

    def form_valid(self, form):
        if (form.cleaned_data['has_household_benefits'] == 'True'):
            self.success_url = '/apply/eligibility/'
        return super().form_valid(form)


class HouseholdContributorsView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/household-contributors.html'
    form_class = forms.HouseholdContributorsForm
    success_url = '/apply/income/'

    def form_valid(self, form):
        if (int(form.cleaned_data['household_contributors']) == 1):
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

    def form_valid(self, form):
        if self.request.session['has_job'] == 'True' or form.cleaned_data['is_self_employed'] == 'True':
            self.success_url = '/apply/number-of-jobs/'
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

class IncomeMethodsView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/income-methods.html'
    form_class = forms.IncomeMethodsForm
    success_url = '/apply/income/'

class IncomeView(FormToSessionView, DispatchView):
    success_url = '/apply/other-income-sources/'

    def get_form_class(self):
        """Returns form_class based on income method"""
        income_forms = {
            'exact': forms.ExactIncomeForm,
            'hourly': forms.HourlyIncomeForm,
            'estimate': forms.EstimateIncomeForm
        }
        return income_forms[self.request.session['income_method']]

    def get_template_names(self):
        """Returns template_name based income method"""
        income_method = self.request.session['income_method']
        self.template_name = f'pathways/apply/{income_method}-income.html'
        
        return super().get_template_names()

    def form_valid(self, form):
        """Calculates annual income based on income and pay_period"""
        income = form.cleaned_data['income']
        pay_period = form.cleaned_data['pay_period']

        annual_pay_multipliers = {
            'weekly': 52, 
            'biweekly': 25, 
            'semimonthly': 24,
            'monthly': 12,
            'annually': 1
        }

        if pay_period in annual_pay_multipliers:
            # Not hourly
            annual_income = income * annual_pay_multipliers[pay_period]
        else:
            # Hourly, therefore pay_period is int
            # hourly wage * hours per week * 52 weeks
            annual_income = income * pay_period * 52
        
        self.request.session['income'] = income
        self.request.session['pay_period'] = pay_period
        self.request.session['annual_income'] = annual_income
        
        return super().form_valid(form) 


class OtherIncomeSourcesView(DispatchView, FormToSessionView):
    template_name = 'pathways/apply/other-income-sources.html'
    form_class = forms.OtherIncomeSourcesForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        if form.cleaned_data['has_other_income'] == 'True':
            self.success_url = '/apply/non-job-income/'
        return super().form_valid(form)


class NonJobIncomeView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/non-job-income.html'
    form_class = forms.NonJobIncomeForm
    success_url = '/apply/review-eligibility/'

    def form_valid(self, form):
        if 'annual_income' in self.request.session.keys():
            # Applicant has already entered job-based income
            # Their (monthly) non_job_income will be added to their existing annual income
            annual_income = self.request.session['annual_income']
            non_job_income = form.cleaned_data['non_job_income']
            self.request.session['annual_income'] = annual_income + (12 * non_job_income)
        else:
            # Applicant does NOT have job-based income, therefore only income is non-job-based
            self.request.session['annual_income'] = form.cleaned_data['non_job_income']
        return super().form_valid(form)


class ReviewEligibilityView(DispatchView):
    template_name = 'pathways/apply/review-eligibility.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale.setlocale( locale.LC_ALL, '' )
        
        # Income
        context['income_formatted'] = '$0'
        if 'income' in self.request.session.keys():
            context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
            
        
        # Non job income
        context['non_job_income_formatted'] = '$0'
        if 'non_job_income' in self.request.session.keys():
            context['non_job_income_formatted'] = '${:,.0f}'.format(self.request.session['non_job_income'])

        # Annual income
        context['annual_income_formatted'] = '$0'
        if 'annual_income' in self.request.session.keys():
            context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])            

        return context
        
# Step 6
class EligibilityView(DispatchView):
    template_name = 'pathways/apply/eligibility.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        income_thresholds = helpers.getIncomeThresholds()

        if self.request.session['has_household_benefits'] == 'True':
            context['is_eligible'] = True
        else:
            if 'annual_income' in self.request.session:
                annual_income = int(self.request.session['annual_income'])
            else:
                annual_income = 0
            max_income = income_thresholds[int(self.request.session['household_size'])]
            context['is_eligible'] = annual_income <= max_income
            locale.setlocale( locale.LC_ALL, '' )
            context['max_income'] = '${:,.0f}'.format(max_income)
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
    success_url = '/apply/review-application/'
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
        # Income
        context['income_formatted'] = '$0'
        if 'income' in self.request.session.keys():
            context['income_formatted'] = '${:,.0f}'.format(self.request.session['income'])
            
        
        # Non job income
        context['non_job_income_formatted'] = '$0'
        if 'non_job_income' in self.request.session.keys():
            context['non_job_income_formatted'] = '${:,.0f}'.format(self.request.session['non_job_income'])

        # Annual income
        context['annual_income_formatted'] = '$0'
        if 'annual_income' in self.request.session.keys():
            context['annual_income_formatted'] = '${:,.0f}'.format(self.request.session['annual_income'])  

        return context

class LegalView(FormToSessionView, DispatchView):
    template_name = 'pathways/apply/legal.html'
    form_class = forms.LegalForm
    success_url = '/apply/refer/'

class ReferralView(FormView, DispatchView):
    template_name = 'pathways/referral.html'
    form_class = forms.ReferralForm
    success_url = '/apply/signature/'

    def form_valid(self, form):
        ref = Referral()
        ref.program = 'Discount'
        for value, text in form.choices:
            setattr(ref, value, form.cleaned_data[value])
        ref.custom_referral = form.cleaned_data['custom_referral']
        ref.save()
        return super().form_valid(form)

class SignatureView(FormView, DispatchView):
    template_name = 'pathways/apply/signature.html'
    form_class = forms.SignatureForm
    success_url = '/apply/documents-overview/'

    def form_valid(self, form):
        self.request.session['signature'] = form.cleaned_data['signature']
        # Removed option of providing account number so people don't think it is absolutely required
        self.request.session['has_account_number'] = 'False'

        # Create new application, load data from session, and save
        app = None
        try:
            app = Application.objects.get(
                household_size=self.request.session['household_size'],
                has_household_benefits=self.request.session['has_household_benefits'],
                first_name=self.request.session['first_name'],
                last_name=self.request.session['last_name'],
                rent_or_own=self.request.session['rent_or_own'],
                street_address=self.request.session['street_address'],
                zip_code=self.request.session['zip_code'],
                phone_number=self.request.session['phone_number'],
                account_holder=self.request.session['account_holder'],
                account_first=self.request.session['account_first'],
                account_last=self.request.session['account_last'],
                legal_agreement=self.request.session['legal_agreement']
            )
            for field in Application._meta.get_fields():
                if field.name == 'email_address' and app.email_address != '':
                    continue
                if field.name in self.request.session:
                    setattr(app, field.name, self.request.session[field.name])

        except ObjectDoesNotExist:
            app = Application()
            for field in Application._meta.get_fields():
                if field.name in self.request.session:
                    setattr(app, field.name, self.request.session[field.name])
        
        app.save()
        self.request.session['app_id'] = app.id

        return super().form_valid(form)

class DocumentOverviewView(DispatchView):
    template_name = 'pathways/docs/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        context['has_household_benefits'] = app.has_household_benefits
        context['rent_or_own'] = app.rent_or_own
        return context

class FormToDocumentView(FormView):
    form_class = forms.DocumentForm
    template_name = 'pathways/docs/upload-form.html'
    
    def form_valid(self, form):
        """Creates new Document object using form data and attaches to current Application"""
        if form.cleaned_data['doc']:
            app = Application.objects.filter(id = self.request.session['app_id'])[0]
            doc = Document()
            doc.application = app
            doc.doc_type = self.doc_type
            doc.save()
            setattr(doc, 'doc_file', form.cleaned_data['doc'])
            doc.save()
        return super().form_valid(form)
        

class DocumentIncomeView(FormToDocumentView, DispatchView):
    success_url = '/apply/documents-residence/'
    extra_context = {'doc_type': 'income'}
    doc_type = 'income'

    def get_form_class(self):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        if str(app.has_household_benefits) == 'True':
            self.doc_type = 'benefits'
            self.extra_context['doc_type'] = 'benefits'
        return self.form_class

    # Document object is created in form_valid() of parent class FormToDocumentView

class DocumentResidenceView(FormToDocumentView, DispatchView):
    success_url = '/apply/confirmation/'
    extra_context = {'doc_type': 'own'}
    doc_type = 'residence'

    def get_form_class(self):
        app = Application.objects.filter(id = self.request.session['app_id'])[0]
        if str(app.rent_or_own) == 'rent':
            self.doc_type = 'rent'
            self.extra_context['doc_type'] = 'rent'
        return self.form_class

    # Document object is created in form_valid() of parent class FormToDocumentView

class ConfirmationView(DispatchView):
    template_name = 'pathways/apply/confirmation.html'
    extra_context = {'confirm_timestamp': datetime.datetime.now().strftime("%m/%d/%Y")}

class LaterDocumentsView(FormView, ClearSessionView):
    template_name = 'pathways/docs/later-docs.html'
    form_class = forms.LaterDocumentsForm
    success_url = '/documents-overview/'
    extra_context = {'card_title': form_class.card_title}

    def form_valid(self, form):
        self.request.session['is_later_docs'] = True

        # Get list of possible application
        app_list = Application.objects.filter(
                first_name__iexact = form.cleaned_data['first_name'],
                last_name__iexact = form.cleaned_data['last_name'],
                zip_code = form.cleaned_data['zip_code'],
                phone_number = form.cleaned_data['phone_number']
                )
                
        if form.cleaned_data['middle_initial'] != '':
            app_list = app_list.filter(middle_initial__iexact = form.cleaned_data['middle_initial'])

        if form.cleaned_data['email_address'] != '':
            app_list = app_list.filter(email_address__iexact = form.cleaned_data['email_address'])

        if len(app_list) == 0:
            # No matching application found
            self.success_url = '/later-documents/no-match-found/'

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
            self.success_url = '/later-documents/more-info-needed/'
            pass

        return super().form_valid(form)

class NoDocumentFoundView(ExtraContextView):
    template_name = 'pathways/docs/no-doc-found.html'

class MoreDocumentInfoRequiredView(FormView):
    template_name = 'pathways/docs/more-doc-info.html'
    form_class = forms.MoreDocumentInfoRequiredForm
    success_url = '/documents-overview/'
    extra_context = {'card_title': form_class.card_title}

    def dispatch(self, request, *args, **kwargs):
        if 'is_later_docs' in request.session:
            return super(MoreDocumentInfoRequiredView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('pathways-home')

    def form_valid(self, form):
        # Get list of possible application
        app_list = Application.objects.filter(
                first_name__iexact = self.request.session['first_name'],
                last_name__iexact = self.request.session['last_name'],
                zip_code = self.request.session['zip_code'],
                phone_number = self.request.session['phone_number'],
                rent_or_own = form.cleaned_data['rent_or_own'],
                street_address__icontains = form.cleaned_data['street_address'],
                household_size = form.cleaned_data['household_size']
                )
        
        if form.cleaned_data['apartment_unit'] != '':
            app_list = app_list.filter(apartment_unit__iexact = form.cleaned_data['apartment_unit'])

        if len(app_list) == 1:
            # Matching application successfully found
            app = app_list[0]
            self.request.session['app_id'] = app.id
            self.request.session['active_app'] = True
        else:
            # No matching application found
            self.success_url = '/later-documents/no-match-found/'

        return super().form_valid(form)