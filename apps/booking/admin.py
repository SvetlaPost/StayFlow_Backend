from django.contrib import admin
from .models import Booking, BookingLog

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'renter', 'rent', 'start_date', 'end_date', 'status', 'commission_amount']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['renter__email', 'rent__title']

@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['booking__id', 'user__email', 'description']
