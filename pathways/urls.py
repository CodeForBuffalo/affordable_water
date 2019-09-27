from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='pathways-home'),
    path('about/', views.about,name='pathways-about'),
    path('apply/', views.HouseholdView.as_view(),
        name='pathways-apply'),
    path('apply/household-eligible/', views.AutoEligibleView.as_view(),
        name='pathways-apply-household-eligible'),
    path('apply/income-methods/', views.IncomeMethodsView.as_view(),
        name='pathways-apply-income-methods'),
    path('apply/exact-income/', views.ExactIncomeView.as_view(),
        name='pathways-apply-exact-income'),
    path('apply/hourly-income/', views.HourlyIncomeView.as_view(),
        name='pathways-apply-hourly-income'),
    path('apply/estimate-income/', views.EstimateIncomeView.as_view(),
        name='pathways-apply-estimate-income'),
    path('apply/review-eligibility/', views.ReviewEligibilityView.as_view(),
        name='pathways-apply-review-eligibility'),
    path('apply/eligibility/', views.EligibilityView.as_view(),
        name='pathways-apply-eligibility'),
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
    path('apply/review-application/', views.ReviewApplicationView.as_view(),
        name='pathways-apply-review-application'),
    path('apply/legal/', views.LegalView.as_view(),
        name='pathways-apply-legal'),
    path('apply/signature/', views.SignatureView.as_view(),
        name='pathways-apply-signature'),
    path('apply/documents/', views.DocumentView.as_view(),
        name='pathways-apply-documents'),
    path('apply/confirmation/', views.ConfirmationView.as_view(),
        name='pathways-apply-confirmation'),
    path('debug/', views.debugsessionview, name='pathways-debug'),
]