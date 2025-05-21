from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district", "state", "country")
    search_fields = ("city", "district", "state")
