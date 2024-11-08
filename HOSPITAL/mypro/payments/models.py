from django.db import models
from django.contrib.auth.models import User
from  myapp.models import *

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=200)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled')
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='booked_user')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    appoinment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=30)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    booking_note = models.CharField(max_length=50)
    booking_total = models.FloatField()
    booking_number = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.booking_number} for {self.first_name} {self.last_name}'
