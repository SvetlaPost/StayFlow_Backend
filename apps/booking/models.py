from django.db import models
from django.conf import settings
from apps.rent.models import Rent

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

    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Calculated platform commission in EUR"
    )

    message = models.TextField(blank=True, help_text="Optional message or request from the renter")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gt=models.F('start_date')), name='booking_dates_valid')
        ]

    def __str__(self):
        return f"Booking #{self.pk} by {self.renter.email} on {self.rent.title}"
