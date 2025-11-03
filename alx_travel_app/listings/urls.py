from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookingViewset, ListingViewset, chapa_payment_gateway, verify_chapa_transaction


router = DefaultRouter()
router.register(r'bookings', BookingViewset, basename='bookings')
router.register(r'listings', ListingViewset, basename='listings')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/', chapa_payment_gateway, name='payment_gateway'),
    path('payments/verify', verify_chapa_transaction, name='verify_payment'),
]