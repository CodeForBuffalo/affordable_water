from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='pathways-home'),
    path('about/', views.about, name='pathways-about'),
    path('apply/', views.ApplicationView.as_view(), name='pathways-apply'),
    path('apply-account/', views.AccountView.as_view(), name='pathways-apply-address')
]