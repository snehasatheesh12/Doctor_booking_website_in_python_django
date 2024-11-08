# signals.py
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn_obj = sender
    # Check if the payment was completed
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Payment was successful
        # Here you can update your database, e.g., mark the order as paid
        invoice_id = ipn_obj.invoice
        # Process the order based on invoice_id or other details
