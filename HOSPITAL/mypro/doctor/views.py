from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User

from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from myapp.models import Contact, Doctor
from django.contrib.auth import logout

from myapp.models import *

def doctor_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('doctor_reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Password Reset Request'
            message = render_to_string('doctor/doctor_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            try:
                send_mail(subject, message, 'snehasatheesh176@gmail.com', [user.email])
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
            return redirect('doctor_forgot_password')
        else:
            messages.error(request, 'No account found with that email.')
    
    return render(request, 'doctor/doctor_forgot_password.html')

# Reset password
def doctor_reset_password(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset successfully. You can now log in with your new password.')
            return redirect('doct_login_view')  
        return render(request, 'doctor/doctor_reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('doctor_forgot_password')

@login_required
def doctor_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = request.user
        if not check_password(old_password, user.password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'The new passwords do not match.')
        elif not new_password1:
            messages.error(request, 'The new password cannot be empty.')
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('doctor_password_change_done')
    return render(request, 'doctor/doctor_password_change.html')



@login_required
def doctor_profile_view(request):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    return render(request, 'doctor/doctor_profile_view.html', {'profile': doctor_profile})

departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

@login_required
def edit_profile_doctor(request):
    profile = get_object_or_404(Doctor, user=request.user)
    user = request.user 
    if request.method == 'POST':
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        gender = request.POST.get('gender')

        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
            
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()


        profile.mobile = phone
        profile.address = address
        profile.city = city
        profile.state = state
        profile.zip_code = zip_code
        profile.gender = gender
        profile.save()
        return redirect('doctor_dashboard')  
    return render(request, 'doctor/doctor_update_profile.html', {'profile': profile,'department':departments})


@login_required
def delete_profile_doctor(request):
    profile = get_object_or_404(Doctor, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.delete()  
        print(user)
        profile.delete()
        logout(request)   
        return redirect('home_view')
    return render(request, 'doctor/delete_profile.html', {'profile': profile})



def doctor_appointments(request):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    doctor=request.user.id
    appointments = Appointment.objects.filter(doctorId=doctor)
    context = {
        'appointments': appointments,
        'profile':doctor_profile,
    }
    
    return render(request, 'doctor/doctor_appointments.html', context)


def doctor_view_patient(request):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    doctor=request.user.id
    appointments = Appointment.objects.filter(doctorId=doctor)
    context = {
        'appointments': appointments,
        'profile':doctor_profile,
    }
    
    return render(request, 'doctor/view_patient.html', context)