from django.contrib import admin
from .models import Rent

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "title", "owner", "property_type", "location",
        "is_active", "is_daily_available", "is_monthly_available",
        "daily_price", "monthly_price", "created_at"
    )
    list_filter = ("is_active", "property_type", "is_daily_available", "is_monthly_available", "location__district")
    search_fields = ("title", "location", "description")
    list_editable = ("is_active",)

    @admin.display(description='City')
    def get_city(self, obj):
        return obj.location.city if obj.location else "—"

    @admin.display(description='Country')
    def get_country(self, obj):
        return obj.location.country if obj.location else "—"