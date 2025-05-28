from django.db import models


class Payment(models.Model):
    booking = models.OneToOneField('booking.Booking', on_delete=models.CASCADE, related_name='payment')
    renter = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='host_payments')
    rent = models.ForeignKey('rent.Rent', on_delete=models.SET_NULL, null=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # аренда + комиссия
    base_rent = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # 0.15 - 0.25

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} — {self.renter.email} → {self.host.email}"
