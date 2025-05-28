from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.booking.models import BookingLog
from apps.payments.models import Payment

@transaction.atomic
def process_payment_for_booking(booking):
    city = booking.rent.location.city.lower()
    commission_map = {
        "berlin": Decimal("0.15"),
        "hamburg": Decimal("0.20"),
        "munich": Decimal("0.25"),
    }
    rate = commission_map.get(city, Decimal("0.20"))

    base = booking.base_price
    commission = base * rate
    total = base + commission

    Payment.objects.create(
        booking=booking,
        renter=booking.renter,
        host=booking.rent.owner,
        rent=booking.rent,
        base_rent=base,
        commission_rate=rate,
        commission_amount=commission,
        total_amount=total,
        is_paid=True,
        paid_at=timezone.now()
    )


    booking.status = "confirmed"
    booking.total_price = total
    booking.commission_amount = commission
    booking.commission_percent = rate
    booking.save()

    BookingLog.objects.create(
        booking=booking,
        user=booking.rent.owner,
        action="update",
        description=f"Booking confirmed and payment recorded. Total: {total} EUR"
    )