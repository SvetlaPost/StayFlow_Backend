from django.contrib import admin
from .models import Booking, BookingLog


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'renter',
        'rent',
        'rent_id',
        'host_email',
        'start_date',
        'end_date',
        'status',
        'commission_amount',
    ]
    list_filter = ['status', 'start_date', 'end_date', 'rent__owner']
    search_fields = ['renter__email', 'rent__title', 'rent__owner__email']
    ordering = ['-start_date']

    @admin.display(description='Rent ID', ordering='rent__id')
    def rent_id(self, obj):
        return obj.rent.id if obj.rent else None

    @admin.display(description='Host Email', ordering='rent__owner__email')
    def host_email(self, obj):
        return obj.rent.owner.email if obj.rent and obj.rent.owner else '—'


@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['booking__id', 'user__email', 'description']
