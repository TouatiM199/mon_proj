from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_certificates, name='generate_certificates')
]
