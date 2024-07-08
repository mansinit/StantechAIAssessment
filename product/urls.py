from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('signup/',views.signup),
    path('login/',views.login),
    path('download_summary_report/',views.download_summary_report),
    path('display/',views.display_summary_report),
]