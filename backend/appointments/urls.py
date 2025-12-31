# appointments/urls.py
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Appointments
    path('', views.appointment_list_create, name='appointment-list-create'),
    path('<uuid:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('<uuid:appointment_id>/status/', views.update_appointment_status, name='appointment-status'),
    path('available-inspectors/', views.available_inspectors, name='available-inspectors'),
    
    # Inspector Schedule/Calendar
    path('inspector-schedule/', views.inspector_schedule, name='inspector-schedule-self'),
    path('inspector-schedule/<uuid:inspector_id>/', views.inspector_schedule, name='inspector-schedule'),
    
    # Reschedule
    path('needs-reschedule/', views.appointments_needing_reschedule, name='needs-reschedule'),
    path('<uuid:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule'),
    
    # Call Tasks (Call Center Admin)
    path('tasks/', views.call_task_list_create, name='task-list-create'),
    path('tasks/<uuid:task_id>/', views.call_task_detail, name='task-detail'),
    path('clients-needing-inspection/', views.clients_needing_inspection, name='clients-needing-inspection'),
    path('call-centers/', views.list_call_centers, name='list-call-centers'),
]
