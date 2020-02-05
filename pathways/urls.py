from django.urls import path
from django.conf.urls.i18n import i18n_patterns

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='pathways-home'),
    path('about/', views.AboutView.as_view(),name='pathways-about'),
    path('nondiscrimination/', views.NonDiscriminationView.as_view(),                                     name='pathways-nondsicrimination'),
    path('apply/', views.ApplyView.as_view(),
        name='pathways-apply'),
    # Household
    path('apply/household-size/', views.HouseholdSizeView.as_view(),
        name='pathways-apply-household-size'),
    path('apply/household-benefits/', views.HouseholdBenefitsView.as_view(),
        name='pathways-apply-household-benefits'),
    # Income
    path('apply/household-contributors/', views.HouseholdContributorsView.as_view(),
        name='pathways-apply-household-contributors'),
    path('apply/job-status/', views.JobStatusView.as_view(),
        name='pathways-apply-job-status'),
    path('apply/self-employment/', views.SelfEmploymentView.as_view(),
        name='pathways-apply-self-employment'),
    path('apply/other-income-sources/', views.OtherIncomeSourcesView.as_view(),
        name='pathways-apply-other-income-sources'),
    path('apply/number-of-jobs/', views.NumberOfJobsView.as_view(),
        name='pathways-apply-number-of-jobs'),
    path('apply/non-job-income/', views.NonJobIncomeView.as_view(),
        name='pathways-apply-non-job-income'),
    path('apply/income-methods/', views.IncomeMethodsView.as_view(),
        name='pathways-apply-income-methods'),
    path('apply/income/', views.IncomeView.as_view(),
        name='pathways-apply-income'),
    # Eligibility
    path('apply/review-eligibility/', views.ReviewEligibilityView.as_view(),
        name='pathways-apply-review-eligibility'),
    path('apply/eligibility/', views.EligibilityView.as_view(),
        name='pathways-apply-eligibility'),
    # Additional Info
    path('apply/additional-questions/', views.AdditionalQuestionsView.as_view(),
        name='pathways-apply-additional-questions'),
    path('apply/resident-info/', views.ResidentInfoView.as_view(),
        name='pathways-apply-resident-info'),
    path('apply/account-holder/', views.AccountHolderView.as_view(),
        name='pathways-apply-account-holder'),
    path('apply/address/', views.AddressView.as_view(),
        name='pathways-apply-address'),
    path('apply/contact-info/', views.ContactInfoView.as_view(),
        name='pathways-apply-contact-info'),
    path('apply/account-number/', views.AccountNumberView.as_view(),
        name='pathways-apply-account-number'),
    # Review and sign
    path('apply/review-application/', views.ReviewApplicationView.as_view(),
        name='pathways-apply-review-application'),
    path('apply/legal/', views.LegalView.as_view(),
        name='pathways-apply-legal'),
    path('apply/signature/', views.SignatureView.as_view(),
        name='pathways-apply-signature'),
    # Documents
    path('apply/documents-overview/', views.DocumentOverviewView.as_view(),
        name='pathways-apply-documents-overview'),
    path('apply/documents-income/', views.DocumentIncomeView.as_view(),
        name='pathways-apply-documents-income'),
    path('apply/documents-residence/', views.DocumentResidenceView.as_view(),
        name='pathways-apply-documents-residence'),
    path('apply/confirmation/', views.ConfirmationView.as_view(),
        name='pathways-apply-confirmation'),
    path('apply/later-documents/', views.LaterDocumentsView.as_view(),
        name='pathways-apply-later-documents'),
    path('apply/later-documents/no-match-found/', views.NoDocumentFoundView.as_view(),
        name='pathways-apply-later-documents-not-found'),
    path('apply/later-documents/more-info-needed/', views.MoreDocumentInfoRequiredView.as_view(),
        name='pathways-apply-later-documents-more-info')
]