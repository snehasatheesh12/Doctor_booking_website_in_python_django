from django.contrib import admin
from django.urls import path
from payments import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


urlpatterns = [
    path('admin/', admin.site.urls),
    path('place_order/<int:appointment_id>/', views.place_order, name='place_order'),
    path('checkout/',views.checkout,name='checkout'),
    path('api/paypal/order/create/', views.create_paypal_order, name='create_paypal_order'),
    path('api/paypal/order/<str:order_id>/capture/', views.capture_paypal_order, name='capture_paypal_order'),
    path('place_order/api/transaction/receive/', views.receive_transaction_details, name='receive_transaction'),
  
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

