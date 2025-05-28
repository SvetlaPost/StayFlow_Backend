from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.rent.models import Rent

COMMISSION_BY_CITY = {
    "Berlin": Decimal("0.25"),
    "Munich": Decimal("0.25"),
    "Hamburg": Decimal("0.20"),
    "Cologne": Decimal("0.18"),
    "Leipzig": Decimal("0.15"),
    # default = 0.15
}
DEFAULT_COMMISSION = Decimal("0.15")

def get_commission_rate(city: str) -> Decimal:
    return COMMISSION_BY_CITY.get(city, Decimal("0.15"))

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="User who made the booking"
    )
    rent = models.ForeignKey(
        Rent,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Rental listing that was booked"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Price without commission",

    )
    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.15"),
        help_text="0.15 = 15%"
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Calculated platform commission in EUR"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="base + commission"
    )

    message = models.TextField(blank=True, help_text="Optional message or request from the renter")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gt=models.F('start_date')), name='booking_dates_valid')
        ]


    def save(self, *args, **kwargs):

        if not self.rent or self.rent.daily_price is None or self.rent.daily_price <= Decimal("0.00"):
            raise ValidationError("Rent must have a valid daily price greater than 0.")

        nights = (self.end_date - self.start_date).days or 1
        self.base_price = self.rent.daily_price * nights

        city = self.rent.location.city.lower() if self.rent.location and self.rent.location.city else ""
        high_economy_cities = ['berlin', 'munich', 'hamburg', 'frankfurt', 'stuttgart']

        self.commission_percent = Decimal("0.25") if city in high_economy_cities else Decimal("0.15")
        self.commission_amount = self.base_price * self.commission_percent
        self.total_price = self.base_price + self.commission_amount

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Booking #{self.pk} by {self.renter.email} on {self.rent.title}"

class BookingLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('cancel', 'Cancelled'),
        ('update', 'Updated'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)


    def __str__(self):
        return f"{self.action} on booking #{self.booking.id} by {self.user}"

