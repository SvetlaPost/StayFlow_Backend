from django.contrib import admin
from apps.reviews.models import Rating  # или Review, если у тебя такое имя модели

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "renter", "stars", "comment", "created_at")
    list_filter = ("stars", "created_at")
    search_fields = ("booking__id", "renter__email", "comment")
    readonly_fields = ("created_at",)
