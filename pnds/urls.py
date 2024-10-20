from django.urls import path
from . import views

app_name = 'pnds'

urlpatterns = [
    path('', views.index),
]
