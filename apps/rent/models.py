#from django.db import models


#class Rent(models.Model):
#    title = models.CharField(max_length=90)
#    description = models.TextField()
#    address = # id  со ссылкой на отдельный класс адреса
#    price = models.DecimalField(
#        max_digits=6,
#        decimal_places=2
#    )
#    rooms_count = models.PositiveIntegerField()
#    room_type = models.CharField(
#        max_length=40,
#        choises=RoomType.choices()
#    )

from apps.rent.choices.room_type import RoomType
from apps.users.models import User
from django.db import models

class RentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Rent(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rents')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveIntegerField()
    property_type = models.CharField(
        max_length=50,
        choices=[(rt.name, rt.value) for rt in RoomType],
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    is_daily_available = models.BooleanField(default=False)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_monthly_available = models.BooleanField(default=False)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RentManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.title} — {self.location}"
