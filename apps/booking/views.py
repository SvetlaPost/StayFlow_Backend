from datetime import date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.booking import models
from apps.booking.models import Booking, BookingLog
from apps.booking.permissions import IsBookingOwnerOrAdmin, IsBookingRelatedOrAdmin
from apps.booking.serializers import BookingSerializer
from apps.booking.utils import send_booking_notification

from django.db.models import Q, Count, Avg

from decimal import Decimal

from rest_framework.exceptions import NotFound

from apps.payments.services import process_payment_for_booking
from apps.rent.models import Rent
from apps.users.models import User


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingRelatedOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(Q(renter=user) | Q(rent__owner=user)).distinct()

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        booking_id = self.kwargs.get(lookup_url_kwarg)

        try:
            obj = Booking.objects.select_related("rent", "renter").get(pk=booking_id)
        except Booking.DoesNotExist:
            raise NotFound("Booking not found.")

        user = self.request.user
        print(f"[DEBUG] get_object called: booking #{obj.id}, requested by {user.email}, "
              f"is_staff={user.is_staff}, is_host={user.is_host}, renter_id={obj.renter_id}, rent_owner_id={obj.rent.owner_id}")

        if user.is_staff:
            return obj
        if user.is_host and obj.rent.owner_id == user.id:
            return obj
        if obj.renter_id == user.id:
            return obj

        raise PermissionDenied("You do not have permission to view this booking.")

    def log_booking_action(self, booking, user, action, description=""):
        BookingLog.objects.create(
            booking=booking,
            user=user,
            action=action,
            description=description,
        )



    def perform_create(self, serializer):
        rent = serializer.validated_data['rent']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        commission = self.calculate_commission(rent, start_date, end_date)

      #  conflict = Booking.objects.filter(
      #      rent=rent,
      #      status__in=["pending", "confirmed"],
      #      start_date__lt=end_date,
      #      end_date__gt=start_date
      #  ).exists()
#
      #  if conflict:
      #      raise ValidationError("These dates are already booked or temporarily reserved by another user.")

        booking = serializer.save(
            renter=self.request.user,
            commission_amount=commission,
            status='pending'
        )


        host_msg = send_booking_notification(booking, to_host=True)
        renter_msg = send_booking_notification(booking, to_host=False)

        self.created_booking = booking
        self.host_msg = host_msg
        self.renter_msg = renter_msg

        message = (
            f"Dear {booking.renter.full_name},\n\n"
            f"The booking request for '{booking.rent.title}' from {booking.start_date} to {booking.end_date} "
            f"has been received and is currently **pending**.\n"
            f"These dates are now marked as temporarily reserved until the host takes action.\n\n"
            f"Thank you for using our platform!"
        )
        print(f"[Notification to renter] {message}")

        self.created_message = message

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, "created_booking"):
            response.data['notification_host'] = self.host_msg
            response.data['notification_renter'] = self.renter_msg
            response.data['info'] = "Other users will be blocked from booking the same dates."
        return response

    def calculate_commission(self, rent, start_date, end_date):
        total_days = (end_date - start_date).days or 1
        daily_price = rent.daily_price or Decimal("0")
        return round(daily_price * Decimal(total_days) * Decimal("0.1"), 2)

    @swagger_auto_schema(
        operation_summary="Create a booking",
        operation_description="Creates a booking and automatically calculates a 10% commission fee.",
        responses={201: BookingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, "created_booking"):
            response.data['notification_host'] = self.host_msg
            response.data['notification_renter'] = self.renter_msg
            response.data['info'] = "Other users will be blocked from booking the same dates."
        return response

    def perform_destroy(self, instance):
        user = self.request.user
        self.log_booking_action(instance, user, "cancel", "Booking canceled.")

        if user == instance.renter:
            days_before = (instance.start_date - date.today()).days

            if instance.status == 'pending':
                instance.delete()
                print(
                    f"[PENDING CANCELLED] Booking #{instance.id} by {user.email} for '{instance.rent.title}' "
                    f"({instance.start_date} → {instance.end_date}) has been deleted."
                )
                return

            if days_before >= 3:
                commission = self.calculate_commission(instance.rent, instance.start_date, instance.end_date)
                instance.delete()
                raise PermissionDenied(f"Booking canceled. 10% commission: {commission}€ will be withheld.")
            else:
                raise PermissionDenied("You can cancel only at least 3 days in advance.")

        if user.is_staff:
            instance.delete()
        else:
            raise PermissionDenied("Only the renter, owner or admin can cancel this booking.")


    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm_booking(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        if user != booking.rent.owner and not user.is_staff:
            return Response({"detail": "Only the host or admin can confirm this booking."},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.status != "pending":
            return Response({"detail": "Booking is not in pending state."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            process_payment_for_booking(booking)
            booking.refresh_from_db()
        except Exception as e:
            return Response(
                {"detail": f"Payment creation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        overlapping_pending = Booking.objects.filter(
            rent=booking.rent,
            status="pending",
            start_date__lt=booking.end_date,
            end_date__gt=booking.start_date
        ).exclude(pk=booking.pk)

        for b in overlapping_pending:
            b.status = "cancelled"
            b.save()
            send_booking_notification(b, to_host=False, cancelled=True)

        send_booking_notification(booking, to_host=False)

        return Response(
            {"detail": "Booking confirmed and payment recorded. Other pending bookings have been declined."},
            status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.rent.owner and not request.user.is_staff:
            return Response({"detail": "Only the host or admin can cancel this booking."},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.status == "cancelled":
            return Response({"detail": "Booking is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = "cancelled"
        booking.save()

        send_booking_notification(booking, to_host=False, cancelled=True)

        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)


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


class AdminHostStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        hosts = User.objects.filter(is_host=True)

        data = []

        for host in hosts:
            rents = Rent.objects.filter(owner=host)
            total_rents = rents.count()

            bookings = Booking.objects.filter(rent__in=rents)
            total_bookings = bookings.count()
            confirmed_bookings = bookings.filter(status="confirmed").count()
            avg_price = rents.aggregate(avg=Avg("daily_price"))["avg"] or 0

            data.append({
                "host_id": host.id,
                "email": host.email,
                "full_name": host.full_name,
                "total_rents": total_rents,
                "total_bookings": total_bookings,
                "confirmed_bookings": confirmed_bookings,
                "avg_daily_price": round(avg_price, 2)
            })

        return Response(data)



