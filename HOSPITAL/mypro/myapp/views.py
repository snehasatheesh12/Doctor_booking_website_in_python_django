from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from account.views import admin_required, is_admin
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from account.models import *
from django.conf import settings
 # Make sure the Subscribe model is correctly imported

def home_view(request):
    # Check if it's a POST request (form submission)
    if request.method == 'POST':
        # Extract email from POST data
        email = request.POST.get('email')
        
        # Create a new subscription entry
        m = Subscribe.objects.create(email=email, status=True)
        m.save()

        # Add a success message for the user
        messages.info(request, 'Thank you for subscribing!')

        # Prepare the email message
        subject = 'Subscription Added'
        message = (
            f"Dear {email},\n\n"
            f"Thank you for subscribing to our healthcare updates and services! We're excited to keep you informed about the latest health tips, wellness programs, and exclusive offers.\n\n"
            f"As part of your subscription, you'll receive personalized content tailored to your healthcare needs, as well as reminders about upcoming health screenings, consultations, and special events.\n\n"
            "If you have any questions or would like to update your preferences, feel free to reach out to us at any time.\n\n"
            "Thank you for trusting us with your health and wellness journey.\n\n"
            "Best regards,\n"
            "The Healthcare Team"
        )

        from_email = 'snehasatheesh176@gmail.com'
        recipient_list = [email]  # Recipient's email

        # Send the email using send_mail
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")

    # Render the home page
    return render(request, 'index.html')



def admin_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('admin_reset_password', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Password Reset Request'
            message = render_to_string('admin/admin_reset_email.html', {
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
    
    return render(request, 'admin/admin_forgot_password.html')

# Reset password
def admin_reset_password(request, uidb64, token):
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
            return redirect('admin_login_view')  
        return render(request, 'admin/admin_reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('admin_forgot_password')

@login_required
def admin_change_password(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
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
            return redirect('admin_password_change_done')
    return render(request, 'admin/admin_password_change.html',{'profile':profile})




@login_required
def admin_profile_view(request):
    admin_profile = get_object_or_404(MyAdmin, user=request.user)
    return render(request, 'admin/admin_profile_view.html', {'profile': admin_profile})


@login_required
def edit_profile_admin(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
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
        return redirect('admin_dashboard')  
    return render(request, 'admin/admin_update_profile.html', {'profile': profile})


@login_required
def delete_profile_admin(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.delete()  
        print(user)
        profile.delete()
        logout(request)   
        return redirect('home_view')
    return render(request, 'admin/delete_profile.html', {'profile': profile})


@login_required(login_url='adminlogin')
@admin_required
def admin_approve_doctor_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    doctors=Doctor.objects.all().filter(status=False)
    return render(request,'admin/admin_approve_doctor.html',{'doctors':doctors,'profile':profile})


@login_required(login_url='adminlogin')
@admin_required
def approve_doctor_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin_approve_doctor_view'))


@login_required(login_url='adminlogin')
@admin_required
def reject_doctor_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    user=User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin_approve_doctor_view')


@login_required(login_url='adminlogin')
@admin_required
def admin_view_doctor_specialisation_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    doctors=Doctor.objects.all().filter(status=True)
    return render(request,'admin/admin_view_doctor_specialisation.html',{'doctors':doctors,'profile':profile})


@login_required(login_url='adminlogin')
@admin_required
def admin_view_doctor_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    doctors=Doctor.objects.all().filter(status=True)
    return render(request,'admin/admin_view_doctor.html',{'doctors':doctors,'profile':profile})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    user=User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin_view_doctor_view')

    
departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        profile_pic = request.FILES.get('profile_pic')
        confirm_password = request.POST.get('confirm_password')

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
            doctor = Doctor(
                user=user,
                address=address,
                mobile=mobile,
                department=department,
                profile_pic=profile_pic,
                status=True  
            )
            doctor.save()
            my_doctor_group, created = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group.user_set.add(user)
            return HttpResponseRedirect('admin_view_doctor_view')
    return render(request, 'admin/admin_add_doctor.html',{'departments': departments,'profile':profile})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_update_doctor_view(request, pk):
    profile = get_object_or_404(MyAdmin, user=request.user)
    doctor = Doctor.objects.get(id=pk)
    user = User.objects.get(id=doctor.user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        profile_pic = request.FILES.get('profile_pic')
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        if password:
            user.set_password(password)
        user.save()
        doctor.address = address
        doctor.mobile = mobile
        doctor.department = department
        if profile_pic:
            doctor.profile_pic = profile_pic
        doctor.status = True
        doctor.save()

        return redirect('admin_view_doctor_view')
    
    context = {
        'doctor': doctor,  
        'user': user, 
        'department': departments,
        'profile':profile
    }
    return render(request, 'admin/admin_update_doctor.html', context)

#////admin-patient view//////////////////////



@login_required(login_url='adminlogin')
@admin_required
def admin_view_patient_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    patient=Patient.objects.all()
    return render(request,'admin/admin_view_patient.html',{'patient':patient,'profile':profile})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin_view_patient_view')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    profile = get_object_or_404(MyAdmin, user=request.user)
    appointments=Appointment.objects.all().filter(status=False)
    return render(request,'admin/admin_approve_appointment.html',{'appointments':appointments,'profile':profile})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request, pk):
    appointment = Appointment.objects.get(id=pk)
    patient = Patient.objects.get(user_id=appointment.patientId)
    
    # Update appointment status
    appointment.status = True
    appointment.save()

    # Prepare the email message
    subject = 'Appointment Approval Confirmation'
    message = (
        f"Dear {patient.user.first_name},\n\n"
        f"We are pleased to inform you that your appointment with Dr. {appointment.doctorName} scheduled for {appointment.appointmentDate} at {appointment.appointmentTime} has been approved.\n\n"
        "We look forward to seeing you at the scheduled time. If you have any questions or need to reschedule, please contact us.\n\n"
        "Thank you for choosing our healthcare service.\n\n"
        "Best regards,\n"
        "The Healthcare Team"
    )
    from_email = 'snehasatheesh176@gmail.com'
    recipient_list = [patient.user.email]  # Patient's email

    # Send the email notification
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request, pk):
    appointment = Appointment.objects.get(id=pk)
    patient = Patient.objects.get(user_id=appointment.patientId)

    # Prepare the email message
    subject = 'Appointment Rejection Notice'
    message = (
        f"Dear {patient.user.first_name},\n\n"
        f"We regret to inform you that your appointment with Dr. {appointment.doctorName} scheduled for {appointment.appointmentDate} at {appointment.appointmentTime} has been rejected.\n\n"
        "We apologize for any inconvenience this may cause. If you have any questions or need further assistance, please feel free to contact us.\n\n"
        "Thank you for your understanding.\n\n"
        "Best regards,\n"
        "The Healthcare Team"
    )
    from_email = 'snehasatheesh176@gmail.com'
    recipient_list = [patient.user.email]  
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    appointment.delete()

    return redirect('admin-approve-patient')

# views.py

def doctor(request):
    m=Doctor.objects.filter(status=True)
    p={'m':m}
    return render(request,'doctors.html',p)

def portfolio(request):
    return render(request,'portfolio-details.html')