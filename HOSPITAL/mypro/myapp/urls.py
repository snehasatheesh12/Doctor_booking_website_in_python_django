"""
URL configuration for mypro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view,name='home_view'),
    path('is_admin', views.is_admin,name='is_admin'),
    path('admin_approve_doctor_view', views.admin_approve_doctor_view,name='admin_approve_doctor_view'),
    path('approve_doctor_view/<int:pk>', views.approve_doctor_view,name='approve_doctor_view'),
    path('reject_doctor_view/<int:pk>', views.reject_doctor_view,name='reject_doctor_view'),
    path('admin_view_doctor_specialisation_view', views.admin_view_doctor_specialisation_view,name='admin_view_doctor_specialisation_view'),
    path('admin_view_doctor_view', views.admin_view_doctor_view,name='admin_view_doctor_view'),
    path('admin_add_doctor_view', views.admin_add_doctor_view,name='admin_add_doctor_view'),
    path('delete_doctor_from_hospital_view/<int:pk>', views.delete_doctor_from_hospital_view,name='delete_doctor_from_hospital_view'), 
    path('admin_update_doctor_view/<int:pk>',views.admin_update_doctor_view,name='admin_update_doctor_view'),
    path('admin_view_patient_view', views.admin_view_patient_view,name='admin_view_patient_view'),
    path('delete_patient_from_hospital_view/<int:pk>', views.delete_patient_from_hospital_view,name='delete_patient_from_hospital_view'),
    
    
    path('admin_forgot_password', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin_reset_password/<uidb64>/<token>/', views.admin_reset_password, name='admin_reset_password'),
    path('admin_change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin_password-change-done/', lambda request: render(request, 'admin/admin_password_change_done.html'), name='admin_password_change_done'),
    
    path('admin_profile_view',views.admin_profile_view,name='admin_profile_view'),
    path('edit_profile_admin',views.edit_profile_admin,name='edit_profile_admin'),
    path('delete_profile_admin',views.delete_profile_admin,name='delete_profile_admin'),
    
     path('admin-approve-patient', views.admin_approve_appointment_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_appointment_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_appointment_view,name='reject-patient'),
    path('portfolio',views.portfolio,name='portfolio'),
    path('doctor',views.doctor,name='doctor')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

