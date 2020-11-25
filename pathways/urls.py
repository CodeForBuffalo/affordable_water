from django.urls import path

from pathways import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='pathways-home'),
    path('about/', views.AboutView.as_view(),name='pathways-about'),
    path('nondiscrimination/', views.NondiscriminationView.as_view(), name='pathways-nondiscrimination'),
    path('privacy/', views.PrivacyView.as_view(), name='pathways-privacy'),
    path('metrics/', views.ProgramMetricsView.as_view(), name='pathways-metrics'),
    path('apply/', views.ApplyOverviewAssistanceView.as_view(),
        name='pathways-apply'),
    path('apply/discount-overview/', views.ApplyDiscountView.as_view(),
        name='pathways-apply-discount-overview'),
    # Amnesty Debt Forgiveness
    path('forgive/overview/', views.ForgiveOverviewView.as_view(),
        name='pathways-forgive-overview'),
    path('forgive/city-resident/', views.ForgiveCityResidentView.as_view(),
        name='pathways-forgive-city-resident'),
    path('forgive/additional-questions/', views.ForgiveAdditionalQuestionsView.as_view(),
        name='pathways-forgive-additional-questions'),
    path('forgive/resident-info/', views.ForgiveResidentInfoView.as_view(),
        name='pathways-forgive-resident-info'),
    path('forgive/refer/', views.ForgiveReferralView.as_view(),
        name='pathways-forgive-refer'),
    path('forgive/review-application/', views.ForgiveReviewApplicationView.as_view(),
        name='pathways-forgive-review-application'),
    path('forgive/confirmation/', views.ForgiveConfirmationView.as_view(),
        name='pathways-forgive-confirmation'),
    path('apply/city-resident/', views.CityResidentView.as_view(),
        name='pathways-apply-city-resident'),    
    path('apply/non-resident/', views.NonResidentView.as_view(),
        name='pathways-apply-non-resident'),
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
    path('apply/number-of-jobs/', views.NumberOfJobsView.as_view(),
        name='pathways-apply-number-of-jobs'),
    path('apply/income-methods/', views.IncomeMethodsView.as_view(),
        name='pathways-apply-income-methods'),
    path('apply/income/', views.IncomeView.as_view(),
        name='pathways-apply-income'),
    path('apply/other-income-sources/', views.OtherIncomeSourcesView.as_view(),
        name='pathways-apply-other-income-sources'),
    path('apply/non-job-income/', views.NonJobIncomeView.as_view(),
        name='pathways-apply-non-job-income'),
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
    path('apply/refer/', views.ReferralView.as_view(),
        name='pathways-apply-refer'),
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
    path('later-documents/', views.LaterDocumentsView.as_view(),
        name='pathways-later-documents'),
    path('later-documents/no-match-found/', views.NoDocumentFoundView.as_view(),
        name='pathways-later-documents-not-found'),
    path('later-documents/more-info-needed/', views.MoreDocumentInfoRequiredView.as_view(),
        name='pathways-later-documents-more-info')
]