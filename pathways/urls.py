from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='pathways-home'),
    path('about/', views.about, name='pathways-about'),
    path('apply/', views.apply, name='pathways-apply'),
]