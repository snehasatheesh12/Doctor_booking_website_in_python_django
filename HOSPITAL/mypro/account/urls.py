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
from account import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('patient_signup_view', views.patient_signup_view,name='patient_signup_view'),
    path('patientlogin', views.patientlogin,name='patientlogin'),
    path('patient_dashboard', views.patient_dashboard,name='patient_dashboard'),
    path('is_patient', views.is_patient,name='is_patient'),

    path('admin_signup_view', views.admin_signup_view,name='admin_signup_view'),
    path('admin_login_view', views.admin_login_view,name='admin_login_view'),
    path('is_admin', views.is_admin,name='is_admin'),
    path('afterlogin_view', views.afterlogin_view,name='afterlogin_view'),
    path('admin_dashboard', views.admin_dashboard,name='admin_dashboard'),
    
    

    path('doctor_signup_view', views.doctor_signup_view,name='doctor_signup_view'),
    path('doct_login_view', views.doct_login_view,name='doct_login_view'),
    path('is_doctor', views.is_doctor,name='is_doctor'),
    path('doctor_dashboard', views.doctor_dashboard,name='doctor_dashboard'),
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    path('patientclick_view',views.patientclick_view,name='patientclick_view'),
    path('handel_logout',views.handel_logout,name='handel_logout'),
    path('contact',views.contact,name='contact'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

