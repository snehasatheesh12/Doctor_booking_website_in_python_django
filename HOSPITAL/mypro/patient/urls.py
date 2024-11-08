
from django.contrib import admin
from django.urls import path
from patient import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


urlpatterns = [
    path('patient_forgot_password', views.patient_forgot_password, name='patient_forgot_password'),
    path('patient_reset-password/<uidb64>/<token>/', views.patient_reset_password, name='patient_reset_password'),
    path('patient_change-password/', views.patient_change_password, name='patient_change_password'),
    path('patient_password-change-done/', lambda request: render(request, 'patient/patient_password_change_done.html'), name='patient_password_change_done'),
    path('patient_profile_view',views.patient_profile_view,name='patient_profile_view'),
    path('edit_profile_patient',views.edit_profile_patient,name='edit_profile_patient'),
    path('delete_profile_patient',views.delete_profile_patient,name='delete_profile_patient'),
    path('patient_book_appointment_view',views.patient_book_appointment_view,name='patient_book_appointment_view'),
    path('appointments/', views.patient_appointments_view, name='patient-appointments'),
    path('view-available-doctors/', views.view_available_doctors, name='view-available-doctors'),
    path('patient_view_doctor_specialisation_view',views.patient_view_doctor_specialisation_view,name='patient_view_doctor_specialisation_view'),
    path('patient_orders',views.patient_orders,name='patient_orders')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

