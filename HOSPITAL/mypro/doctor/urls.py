
from django.contrib import admin
from django.urls import path
from doctor import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

urlpatterns = [
    path('doctor_forgot_password', views.doctor_forgot_password, name='doctor_forgot_password'),
    path('doctor_reset-password/<uidb64>/<token>/', views.doctor_reset_password, name='doctor_reset_password'),
    path('doctor_change-password/', views.doctor_change_password, name='doctor_change_password'),
    path('doctor_password-change-done/', lambda request: render(request, 'doctor/doctor_password_change_done.html'), name='doctor_password_change_done'),
    path('doctor_profile_view',views.doctor_profile_view,name='doctor_profile_view'),
    path('edit_profile_doctor',views.edit_profile_doctor,name='edit_profile_doctor'),
    path('delete_profile_doctor',views.delete_profile_doctor,name='delete_profile_doctor'),
    path('doctor_appointments', views.doctor_appointments, name='doctor_appointments'),
    path('doctor_view_patient', views.doctor_view_patient, name='doctor_view_patient'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

