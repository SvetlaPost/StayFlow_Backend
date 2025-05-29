from django.db import models
from django.conf import settings

class Rating(models.Model):
    booking = models.OneToOneField("booking.Booking", on_delete=models.CASCADE, related_name="rating")
    rent = models.ForeignKey("rent.Rent", on_delete=models.CASCADE, related_name="ratings")
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    stars = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking', 'renter')

    def __str__(self):
        return f"Rating {self.stars}★ for booking #{self.booking.id}"
