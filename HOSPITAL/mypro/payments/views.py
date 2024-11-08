from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from myapp.models import *
import datetime
import datetime
from django.contrib.auth.decorators import login_required

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect


def place_order(request, appointment_id):
    current_user = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.status:
        return render(request, 'patient/booking.html', {'message': 'The appointment is not approved yet.'})

    if request.method == 'POST':
        existing_order = Order.objects.filter(user=current_user, appoinment=appointment).first()
        if existing_order:
            return render(request, 'patient/place_order.html', {'order': existing_order, 'appointment': appointment})

        # Collect form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phonenumber')
        address_line1 = request.POST.get('addressline1')
        address_line2 = request.POST.get('addressline2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        booking_note = request.POST.get('ordernote')
        booking_total = request.POST.get('amount')
        ip = request.META.get('REMOTE_ADDR')

        # Generate the current date for booking number
        yr = int(datetime.datetime.today().strftime('%Y'))
        dt = int(datetime.datetime.today().strftime('%d'))
        mt = int(datetime.datetime.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime('%Y%m%d')

        # Create a new order
        order = Order.objects.create(
            user=current_user,
            appoinment=appointment,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone_number,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            country=country,
            booking_note=booking_note,
            booking_total=booking_total,
            ip=ip
        )

        booking_number = current_date + str(order.id)
        order.booking_number = booking_number
        order.save()
        return render(request, 'patient/place_order.html', {'order': order, 'appointment': appointment})
    return render(request, 'patient/booking.html')



def checkout(request):
    return render(request,'patient/place_order.html',)


def create_order_with_paypal(amount):
    client_id = 'ARQ65oYr2XSWyrI14W-miP4nXCjA496XZyBRPzxUY8W1GJhiaGH5kWeJwIwnVNbe1qij70XxZsdMBxmm'
    secret = 'EM_4v8bAdMXaEmKWeSojqIt5eEpEOEXuaq7aZCCLL6QwdoVvtTsuoS8e0yHnt5lMFcU6dXJx3kpQBBSH'
    api_url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'

    response = requests.post(
        'https://api-m.sandbox.paypal.com/v1/oauth2/token',
        auth=(client_id, secret),
        data={'grant_type': 'client_credentials'}
    )

    if response.status_code != 200:
        return {'error': 'Failed to get access token', 'details': response.json()}

    access_token = response.json().get('access_token')

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": amount
            }
        }]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    order_response = requests.post(api_url, json=order_data, headers=headers)

    if order_response.status_code != 201:
        return {'error': 'Failed to create order', 'details': order_response.json()}

    return order_response.json()


@csrf_exempt
def create_paypal_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        print(data)

        order_response = create_order_with_paypal(amount)

        if 'error' in order_response:
            return JsonResponse(order_response, status=400)  # Return error details with a 400 status

        return JsonResponse({'id': order_response.get('id')})  # Return the order ID
    return JsonResponse({'id': order_response.get('id')})  # Return the order ID



@csrf_exempt  # For testing; handle CSRF appropriately in production
def capture_paypal_order(request, order_id):
    if request.method == 'POST':
        # Set your PayPal API credentials
        client_id = 'ARQ65oYr2XSWyrI14W-miP4nXCjA496XZyBRPzxUY8W1GJhiaGH5kWeJwIwnVNbe1qij70XxZsdMBxmm'
        secret = 'EM_4v8bAdMXaEmKWeSojqIt5eEpEOEXuaq7aZCCLL6QwdoVvtTsuoS8e0yHnt5lMFcU6dXJx3kpQBBSH'
        api_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'

        # Get an access token
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            auth=(client_id, secret),
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get access token', 'details': response.json()}, status=400)

        access_token = response.json().get('access_token')

        # Capture the order
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        capture_response = requests.post(api_url, headers=headers)

        if capture_response.status_code != 201:  # 201 Created
            return JsonResponse({'error': 'Failed to capture order', 'details': capture_response.json()}, status=400)

        return JsonResponse(capture_response.json())
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def receive_transaction_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract relevant information from the transaction data
        payment_id = data['purchase_units'][0]['payments']['captures'][0]['id']
        payment_method = 'PayPal'  # Or extract from data if available
        amount_paid = data['purchase_units'][0]['payments']['captures'][0]['amount']['value']
        status = data['purchase_units'][0]['payments']['captures'][0]['status']
        
        # Create a Payment instance
        payment = Payment(
            user=request.user,  # Ensure the user is authenticated
            payment_id=payment_id,
            payment_method=payment_method,
            amount_paid=amount_paid,
            status=status
        )
        payment.save()  # Save the payment record

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)
