from decimal import Decimal

from rest_framework.exceptions import ValidationError

from apps.core.models import SoftDeleteModel
from apps.rent.choices.room_type import RoomType
from apps.users.models import User
from django.db import models

from apps.location.models import Location
from django.utils import timezone


class RentQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

class RentManager(models.Manager.from_queryset(RentQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Rent(SoftDeleteModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rents',
        help_text="Select the user who is posting the listing (typically a host)."
    )
    title = models.CharField(
        max_length=255,
        help_text="Short title of the listing, e.g., 'Cozy studio in central Berlin'."
    )

    description = models.TextField(
        help_text="Full description of the property: layout, amenities, rental conditions, etc.",
    )

    location = models.ForeignKey(
       Location,
       on_delete=models.CASCADE,
       related_name="rents",
       help_text="Select the location (city/area) where the property is situated."
   )

    rooms = models.PositiveIntegerField(
        help_text="Enter the number of rooms in the property."
    )
    property_type = models.CharField(
        max_length=50,
        choices=[(rt.name, rt.value) for rt in RoomType],
        help_text="Select the type of property: studio, apartment, house, etc."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to temporarily hide this listing from users."
    )

    view_count = models.PositiveIntegerField(default=0)

#    is_deleted = models.BooleanField(default=False)

    is_daily_available = models.BooleanField(
        default=False,
        help_text="Is daily rental available for this property?"
    )
    daily_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Daily rental price in EUR"

    )
    is_monthly_available = models.BooleanField(
        default=False,
        help_text="Price per month (if monthly rental is enabled)."
    )
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    average_rating = models.FloatField(default=0.0)
    ratings_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RentManager()
    all_objects = models.Manager()

    def clean(self):
        if self.is_daily_available:
            if self.daily_price is None:
                raise ValidationError({'daily_price': 'Daily price is required if daily rental is enabled.'})
            if self.daily_price <= Decimal("0.00"):
                raise ValidationError({'daily_price': 'Daily price must be greater than zero.'})

        if self.is_monthly_available:
            if self.monthly_price is None:
                raise ValidationError({'monthly_price': 'Monthly price is required if monthly rental is enabled.'})
            if self.monthly_price < 0:
                raise ValidationError({'monthly_price': 'Monthly price cannot be negative.'})

    def __str__(self):
        try:
            return f"{self.title} — {self.location}"
        except Rent.location.RelatedObjectDoesNotExist:
            return f"{self.title} — No location"


