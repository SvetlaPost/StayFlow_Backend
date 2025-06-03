from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.booking.views import BookingViewSet, MyBookingsView, AdminHostStatsView

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('my/', MyBookingsView.as_view(), name='my-bookings'),
    path("admin/host-stats/", AdminHostStatsView.as_view(), name="admin-host-stats"),
]
