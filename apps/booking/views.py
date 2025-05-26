from datetime import date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from apps.booking import models
from apps.booking.models import Booking
from apps.booking.permissions import IsBookingOwnerOrAdmin, IsBookingRelatedOrAdmin
from apps.booking.serializers import BookingSerializer



class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingRelatedOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(models.Q(renter=user) | models.Q(rent__owner=user)).distinct()

    def perform_create(self, serializer):
        rent = serializer.validated_data['rent']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        commission = self.calculate_commission(rent, start_date, end_date)

        serializer.save(renter=self.request.user, commission_amount=commission)

    def calculate_commission(self, rent, start_date, end_date):
        total_days = (end_date - start_date).days or 1
        daily_price = rent.daily_price or 0
        return round(total_days * daily_price * 0.1, 2)

    @swagger_auto_schema(
        operation_summary="Create a booking",
        operation_description="Creates a booking and automatically calculates a 10% commission fee.",
        responses={201: BookingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user

        if user == instance.renter:
            days_before = (instance.start_date - date.today()).days

            if instance.status == 'pending':
                instance.delete()
                return

            if days_before >= 3:
                commission = self.calculate_commission(instance)
                instance.delete()
                raise PermissionDenied(f"Booking canceled. 10% commission: {commission}€ will be withheld.")
            else:
                raise PermissionDenied("You can cancel only at least 3 days in advance.")

        if user.is_staff:
            instance.delete()
        else:
            raise PermissionDenied("Only owner or admin can cancel this booking.")




class MyBookingsView(ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'start_date']

    def get_queryset(self):
        return Booking.objects.filter(renter=self.request.user)

    @swagger_auto_schema(
        operation_summary="List your own bookings",
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Filter by booking status",
                type=openapi.TYPE_STRING, enum=['pending', 'confirmed', 'cancelled']
            ),
            openapi.Parameter(
                'start_date', openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING, format='date'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
