from django.urls import path
from . import views

app_name = 'pnds'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('<int:pump_id>/', views.pump_view, name = 'pump')
]
