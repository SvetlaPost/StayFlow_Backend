from django.contrib import admin
from .models import Rent

#@admin.register(Rent)
#class RentAdmin(admin.ModelAdmin):
#    list_per_page = 10
#    list_display = (
#        'id', "title", "owner", "property_type", "location",
#        "is_active", "is_daily_available", "is_monthly_available",
#        "daily_price", "monthly_price", "created_at"
#    )
#    list_filter = ('owner', "is_active", "property_type", 'property_type', 'is_active', "is_monthly_available", "location__district")
#    search_fields = ("title", "location", "description", 'owner__email')
#    list_editable = ("is_active",)
#    ordering = ('owner',)
#
#    @admin.display(description='City')
#    def get_city(self, obj):
#        return obj.location.city if obj.location else "—"

from django.contrib import admin
from .models import Rent

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'owner_email', 'property_type',
        'daily_price', 'monthly_price', 'get_city', 'get_district'
    )
    list_filter = ('owner', 'property_type', 'is_active', 'location__city', 'location__district')
    search_fields = ('title', 'owner__email', 'location__city', 'location__district')
    ordering = ('owner',)

    @admin.display(description='Host Email')
    def owner_email(self, obj):
        return obj.owner.email if obj.owner else "-"

    @admin.display(description='City')
    def get_city(self, obj):
        return obj.location.city if obj.location else "—"

    @admin.display(description='Country')
    def get_country(self, obj):
        return obj.location.country if obj.location else "—"

    @admin.display(description='District')
    def get_district(self, obj):
        return obj.location.district if obj.location and obj.location.district else "—"

    @admin.display(description='Country')
    def get_country(self, obj):
        return obj.location.country if obj.location else "—"