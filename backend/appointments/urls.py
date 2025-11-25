# appointments/urls.py
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list_create, name='appointment-list-create'),
    path('<uuid:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('<uuid:appointment_id>/status/', views.update_appointment_status, name='appointment-status'),
    path('available-inspectors/', views.available_inspectors, name='available-inspectors'),
]
