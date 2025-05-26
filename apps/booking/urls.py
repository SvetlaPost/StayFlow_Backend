from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.booking.views import BookingViewSet, MyBookingsView

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/my/', MyBookingsView.as_view(), name='my-bookings'),

]
