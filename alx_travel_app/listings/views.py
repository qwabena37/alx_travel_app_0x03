from rest_framework import viewsets, status, reverse
from django.shortcuts import redirect
from rest_framework.response import Response
import requests
import os
import uuid
from dotenv import load_dotenv
from .serializers import ListingsSerializer, BookingSerializer
from .models import Listings, Booking, Payment
from .tasks import send_booking_confirmation_email


class ListingViewset(viewsets.ModelViewSet):
    queryset = Listings.objects.all()
    serializer_class = ListingsSerializer

class BookingViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            send_booking_confirmation_email.delay(request.user, instance.property)
            return redirect(reverse('payment_gateway'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def chapa_payment_gateway(request, booking_id):
    load_dotenv()

    booking = Booking.objects.filter(id=booking_id) 
    total_amount = booking.listing.price_per_night
    transaction_id = str(uuid.uuid4())

    url = "https://api.chapa.co/v1/transaction/initialize"
    payload = {
    "amount": f"{total_amount}",
    "currency": "ETB",
    "email": "abebech_bekele@gmail.com",
    "first_name": "Bilen",
    "last_name": "Gizachew",
    "phone_number": "0912345678",
    "tx_ref": f"{transaction_id}",
    "callback_url": "https://my_app/payment/callback",
    "return_url": "https://my_app/payment/verify",
    "customization": {
    "title": "Payment test",
    "description": "testing"
    }
    }
    headers = {
    'Authorization': f'Bearer {os.getenv('CHAPA_SECRET_KEY')}',
    'Content-Type': 'application/json'
    }
      
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data["status"] == 'success':
        status='Pending'
        Payment.objects.create(booking=booking, status=status, transaction_id=transaction_id, amount=total_amount)
        checkout_url = data["data"]["checkout_url"]
        return requests.get(checkout_url)
    

def verify_chapa_transaction(request):
    if request.method == 'POST':
        transaction_id = request.get('trx_ref')
        ref_id = request.get('ref_id')
        status = request.get('status')

        payment = Payment.objects.filter(transaction_id=transaction_id)

        payment.status = status.lower()


        
