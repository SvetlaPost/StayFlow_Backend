from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.rent.models import Rent


@receiver(post_save, sender=Rent)
def notify_host_on_rent_creation(sender, instance, created, **kwargs):
    if created:
        print(
            f"[📢 NOTIFICATION] Host '{instance.owner.email}' has created a new listing: '{instance.title}' "
            f"in {instance.location.city}, {instance.location.district or ''}"
        )
