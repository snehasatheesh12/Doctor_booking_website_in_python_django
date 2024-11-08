from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from account.views import is_patient, patient_required
from myapp.models import *
from django.core.mail import send_mail
from django.contrib import messages

from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from payments.models import *


def patient_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('patient_reset_password', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Password Reset Request'
            message = render_to_string('patient/patient_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            try:
                send_mail(subject, message, 'snehasatheesh176@gmail.com', [user.email])
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
            return redirect('patient_forgot_password')
        else:
            messages.error(request, 'No account found with that email.')
    
    return render(request, 'patient/patient_forgot_password.html')

# Reset password
def patient_reset_password(request, uidb64, token):
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
            return redirect('patient_login_view')  
        return render(request, 'patient/patient_reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('patient_forgot_password')

@login_required
def patient_change_password(request):
    patient_profile = get_object_or_404(Patient, user=request.user)

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
            return redirect('patient_password_change_done')
    return render(request, 'patient/patient_password_change.html',{'profile':patient_profile})


@login_required
def patient_profile_view(request):
    patient_profile = get_object_or_404(Patient, user=request.user)
    return render(request, 'patient/patient_profile_view.html', {'profile': patient_profile})


@login_required
def edit_profile_patient(request):
    profile = get_object_or_404(Patient, user=request.user)
    user = request.user  
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone_number')
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
        return redirect('patient_profile_view')  
    return render(request, 'patient/patient_update_profile.html', {'profile': profile})


@login_required
def delete_profile_patient(request):
    profile = get_object_or_404(Patient, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.delete()  
        print(user)
        profile.delete()
        logout(request)   
        return redirect('home_view')
    return render(request, 'patient/delete_profile.html', {'profile': profile})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    
    profile = Patient.objects.get(user_id=request.user.id)  
    doctors = Doctor.objects.filter(status=True)  
    message = None
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctorId')
        symptoms = request.POST.get('symptoms')
        appointmentdate = request.POST.get('appointmentDate')
        appointmenttime = request.POST.get('appointmentTime')
        
        if doctor_id and symptoms:
            doctor = Doctor.objects.get(id=doctor_id)
            
            if doctor.total_tokens > 0:
                assigned_token = doctor.get_next_token()                
                appointment = Appointment(
                    doctorId=doctor.user.id,
                    patientId=request.user.id,
                    doctorName=doctor.user.first_name,
                    patientName=request.user.first_name,
                    status=False,
                    symptoms=symptoms,
                    appointmentDate=appointmentdate,
                    appointmentTime=appointmenttime,
                    assigned_token=assigned_token  
                )
                appointment.save()

                doctor.total_tokens -= 1
                doctor.save()

                message = (
                    f"Dear {request.user.first_name},\n\n"
                    f"Your appointment with Dr. {doctor.user.first_name} has been successfully booked for {appointmentdate} at {appointmenttime}.\n\n"
                    f"Your assigned token number for this appointment is: {assigned_token}\n\n"
                    "Please note that your appointment is currently pending approval. Once the doctor reviews your request, "
                    "you will receive a confirmation email notifying you of the approval status.\n\n"
                    "Thank you for choosing our healthcare service. We look forward to serving you and ensuring a smooth and "
                    "seamless experience. If you have any questions or need further assistance, feel free to reach out to us.\n\n"
                    "Best regards,\n"
                    "The Healthcare Team"
                )

                send_mail(
                    subject='Appointment Confirmation',
                    message=message,
                    from_email='snehasatheesh176@gmail.com',
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.info(request, 'Thank you for the appointment. A confirmation email has been sent.')
            else:
                message = f"Dr. {doctor.user.first_name} is fully booked and has no available tokens."
        else:
            message = "Please fill in all required fields."
  
    mydict = {
        'doctors': doctors,
        'profile': profile,
        'message': message,
        'doctor':doctors
    }
    return render(request, 'patient/patient_add_appoinment.html', context=mydict)


@login_required(login_url='patientlogin')
def patient_appointments_view(request):
    profile = get_object_or_404(Patient, user=request.user)
    patient_appointments = Appointment.objects.filter(patientId=request.user.id).order_by('-appointmentDate')
    context = {
        'appointments': patient_appointments,
        'profile':profile,
    }
    return render(request, 'patient/patient_appointments.html', context)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def view_available_doctors(request):
    profile = get_object_or_404(Patient, user=request.user)
    available_doctors = Doctor.objects.filter(status=True)
    
    context = {
        'doctors': available_doctors,
        'profile':profile
    }
    return render(request, 'patient/view_available_doctors.html', context)


@login_required(login_url='patientlogin')
@patient_required
def patient_view_doctor_specialisation_view(request):
    profile = get_object_or_404(Patient, user=request.user)
    doctors=Doctor.objects.all().filter(status=True)
    return render(request,'patient/patient_view_doctor_specialisation.html',{'doctors':doctors,'profile':profile})

@login_required
def patient_orders(request):
    profile = get_object_or_404(Patient, user=request.user)
    user_orders = Order.objects.filter(user=request.user)

    context = {
        'orders': user_orders,
        'profile':profile,
    }
    return render(request, 'patient/patient_view_orders.html', context)




