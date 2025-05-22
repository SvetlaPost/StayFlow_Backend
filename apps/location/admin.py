from django.contrib import admin
from .models import Location
from django.utils.html import format_html

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district", "state", "country", "latitude", "longitude", "map_link")
    search_fields = ("city", "district", "state")

    @admin.display(description="Map")
    def map_link(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(f"<a href='{url}' target='_blank'>📍 View</a>")
        return "—"
