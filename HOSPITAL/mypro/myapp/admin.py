from django.contrib import admin
from .models import Patient,Doctor,MyAdmin,Appointment


class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic', 'address', 'mobile')

admin.site.register(Patient, PatientAdmin)


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic', 'address', 'mobile')
admin.site.register(Doctor, DoctorAdmin)


class My_Admin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic', 'address', 'mobile')

admin.site.register(MyAdmin, My_Admin)

class Appoinment_Admin(admin.ModelAdmin):
    list_display = ('patientId', 'doctorId', 'patientName', 'doctorName','appointmentDate','status','symptoms')
    
admin.site.register(Appointment,Appoinment_Admin)


class Contact_Admin(admin.ModelAdmin):
    list_display=('name','email','desc','phonenumber','subject')