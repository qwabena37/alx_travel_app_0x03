from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_booking_confirmation_email(guest, listing):
    message = f'''
Dear {guest.username},

Your booking of {listing.name} has been confirmed.
    '''
    send_mail(
        "Booking Confirmation",
        message,
        "airbnb@mail.com",
        [guest.email],
        fail_silently=False,
    )