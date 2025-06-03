from django.contrib import admin
from .models import Rent

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'owner_email', 'property_type', 'is_active',
        'daily_price', 'monthly_price', 'get_city', 'get_district',
        "is_deleted", "created_at",
    )
    actions = ["soft_delete_selected"]
    list_filter = ('owner', 'property_type', 'is_active', 'location__city', 'location__district')
    search_fields = ('title', 'owner__email', 'location__city', 'location__district')
    ordering = ('owner',)

    def get_queryset(self, request):
        return Rent.all_objects.select_related("owner", "location")

    def soft_delete_selected(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete_selected.short_description = "Soft delete selected rentals"

    def has_delete_permission(self, request, obj=None):
        return False

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