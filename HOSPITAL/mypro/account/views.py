from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from myapp.models import Contact, Patient,Doctor,MyAdmin
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.urls import NoReverseMatch,reverse
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
import threading
from django.views import View
from django.shortcuts import get_object_or_404
from .utils import TokenGenerator,generate_token
from django.conf import settings
import uuid  
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def admin_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        profile_pic = request.FILES.get('profile_pic')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        gender = request.POST.get('gender')
        if password==repassword:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')
            user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
            user.set_password(password)
            user.save()
            admin = MyAdmin(user=user, profile_pic=profile_pic,mobile=mobile,address=address,city=city,state=state,gender=gender,zip_code=zip_code)
            admin.save()
            my_admin_group, created = Group.objects.get_or_create(name='ADMIN')
            my_admin_group.user_set.add(user)
            mail_subject='please activate your account'
            current_site=get_current_site(request)
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')   
            return render(request, 'admin/admin-signup.html')
        else:
            messages.error(request, 'password donot match')
    return render(request, 'admin/admin-signup.html')


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.groups.filter(name='ADMIN').exists():
            return HttpResponseRedirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff and user.groups.filter(name='ADMIN').exists():
                login(request, user)
                return redirect('afterlogin_view')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'admin/admin-login.html')

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    elif is_doctor(request.user):
        doctor = Doctor.objects.filter(user_id=request.user.id).first()
        print(doctor)
        if doctor and doctor.status:  
            return redirect('doctor_dashboard')
        else:
            return render(request, 'doctor/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        patient = Patient.objects.filter(user_id=request.user.id).first()
        return redirect('patient_dashboard')
    else:
        return redirect('home_view')


def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff and is_admin(u))(view_func))
    return decorated_view_func


@admin_required
def admin_dashboard(request):
    admin_profile = get_object_or_404(MyAdmin, user=request.user)
    doctor = Doctor.objects.all()
    return render(request, 'admin/admin-dashboard.html',{'profile':admin_profile,'doctor':doctor})


class EmailThread(threading.Thread):
    def __init__(self, send_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.send_email = send_email
        
    def run(self):
        self.send_email.send()
            
departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

def doctor_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        profile_pic = request.FILES.get('profile_pic')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        gender = request.POST.get('gender')
    
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            doctor = Doctor(user=user,department=department, profile_pic=profile_pic,mobile=mobile,address=address,status=False,gender=gender,state=state,city=city,zip_code=zip_code)
            doctor.save()
            my_doctor_group, created = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group.user_set.add(user)
            current_site=get_current_site(request)
            mail_subject='please activate your account'
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')   
    return render(request, 'doctor/doctor-signup.html',{'departments': departments})

def doct_login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='DOCTOR').exists():
            if Doctor.objects.filter(user_id=request.user.id, status=True).exists():
                return redirect('doctor_dashboard')
            else:
                return redirect('afterlogin_view')

    if request.method == 'POST':
        logout(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name='DOCTOR').exists():
                login(request, user)
                return redirect('afterlogin_view') 
            else:
                messages.error(request, 'You do not have doctor privileges.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'doctor/doctor-login.html')


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()

def doctor_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: is_doctor(u))(view_func))
    return decorated_view_func


@doctor_required
def doctor_dashboard(request):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    print(doctor_profile.get_id)
    doctor = Doctor.objects.filter(status='True')
    return render(request, 'doctor/doctor-dashboard.html',{'profile': doctor_profile,'doctor':doctor})


def patient_signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        profile_pic = request.FILES.get('profile_pic')
        email = request.POST.get('email')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        gender = request.POST.get('gender')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            doctor = Patient(user=user, profile_pic=profile_pic,mobile=mobile,address=address,status=False,city=city,state=state,gender=gender,zip_code=zip_code)
            doctor.save()
            my_doctor_group, created = Group.objects.get_or_create(name='PATIENT')
            my_doctor_group.user_set.add(user)
            current_site=get_current_site(request)
            mail_subject='please activate your account'
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')   
    return render(request, 'patient/patient-signup.html',)

def patientlogin(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='PATIENT').exists():
            if Patient.objects.filter(user_id=request.user.id, status=True).exists():
                return redirect('doctor_dashboard')
            else:
                return redirect('afterlogin_view')
    if request.method == 'POST':
        logout(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name='PATIENT').exists():
                login(request, user)
                return redirect('afterlogin_view') 
            else:
                messages.error(request, 'You do not have patient privileges.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'patient/patient-login.html')


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()

def patient_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: is_patient(u))(view_func))
    return decorated_view_func

@patient_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    doctor = Doctor.objects.filter(status=True)
    patient_profile = get_object_or_404(Patient, user=request.user)

    return render(request, 'patient/patient_dashboard.html',{'profile':patient_profile,'doctor':doctor})

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            if user.groups.filter(name='DOCTOR').exists():
                messages.success(request, 'Doctor account activated successfully!')
                return redirect('doct_login_view')  
            elif user.groups.filter(name='PATIENT').exists():
                messages.success(request, 'Patient account activated successfully!')
                return redirect('patientlogin')  
            elif user.groups.filter(name='ADMIN').exists(): 
                messages.success(request, 'Admin account activated successfully!')
                return redirect('admin_login_view')  
        else:
            messages.error(request, 'Activation link is invalid or has expired.')
        return render(request, 'account_verification.html')


def patientclick_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='PATIENT').exists():
           return HttpResponseRedirect('afterlogin_view')
    return render(request, 'patient/patientclick.html')


def handel_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('patientlogin')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Contact.objects.create(name=name, email=email, phonenumber=phone, desc=message, subject=subject)

        from_email = settings.EMAIL_HOST_USER

        email_message = mail.EmailMessage(
            subject=f'Email is from {name}',
            body=f'User Email: {email}\nUser Phone: {phone}\n\n\nQuery:\n{message}',
            from_email=from_email,
            to=['snehasatheesh176@gmail.com']  
        )
        email_client = mail.EmailMessage(
            subject=f'Email is from {name}',
            body=f'User Email: {email}\nUser Phone: {phone}\n\n\nQuery:\n{message}',
            from_email=from_email,
            to=['snehasatheesh176@gmail.com']  
        )
        try:
            email_message.send()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        except Exception as e:
            messages.error(request, f'An error occurred while sending the email: {e}')
        return render(request, 'contact.html')
    return render(request, 'contact.html')



def handel_logout(request):
    if request.user.is_authenticated:
        logout(request)
        if request.user.groups.filter(name='PATIENT').exists():
            return redirect('patientlogin')  
        elif request.user.groups.filter(name='DOCTOR').exists():
            return redirect('doct_login_view')  
        elif request.user.groups.filter(name='ADMIN').exists():
            return redirect('admin_login_view')  
    else:
        return redirect('home_view')  
    return render(request,'index.html')



