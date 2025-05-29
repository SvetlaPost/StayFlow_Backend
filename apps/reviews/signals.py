from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rating

@receiver(post_save, sender=Rating)
def update_rent_rating(sender, instance, **kwargs):
    rent = instance.rent
    all_ratings = rent.ratings.all()
    rent.ratings_count = all_ratings.count()
    rent.average_rating = round(sum(r.stars for r in all_ratings) / rent.ratings_count, 2)
    rent.save()
