from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path, reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Avg, Count, Sum, Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import User
from apps.rent.models import Rent
from apps.booking.models import Booking


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'full_name', 'role', 'is_host', 'is_staff', 'is_active', 'booking_stats')
    list_filter = ('role',)
    ordering = ('id',)

    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_host', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone_number', 'password1', 'password2', 'is_host', 'is_staff', 'is_active', 'role'),
        }),
    )

    search_fields = ('email', 'full_name')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('host-stats/', self.admin_site.admin_view(self.host_stats_view), name="host-stats"),
        ]
        return custom_urls + urls

    def booking_stats(self, obj):
        if not obj.is_host:
            return "-"

        total = Booking.objects.filter(rent__owner=obj).count()
        confirmed = Booking.objects.filter(rent__owner=obj, status='confirmed').count()
        commission = Booking.objects.filter(rent__owner=obj).aggregate(
            total_commission=Sum("commission_amount")
        )['total_commission'] or 0

        url = (
            reverse('admin:booking_booking_changelist')
            + f'?rent__owner__id__exact={obj.id}'
        )

        return mark_safe(
            f'<a href="{url}" title="View bookings for this host">'
            f'{total} total<br>{confirmed} confirmed<br>💰 €{commission:.2f}'
            '</a>'
        )

    booking_stats.short_description = "Booking Stats"
    booking_stats.admin_order_field = 'id'

    def host_stats_view(self, request):
        if not request.user.is_staff:
            return HttpResponse("Forbidden", status=403)

        hosts = User.objects.filter(is_host=True)
        stats = []

        for host in hosts:
            rents = Rent.objects.filter(owner=host)
            bookings = Booking.objects.filter(rent__in=rents)

            stats.append({
                "host": host,
                "total_rents": rents.count(),
                "total_bookings": bookings.count(),
                "confirmed_bookings": bookings.filter(status="confirmed").count(),
                "avg_daily_price": rents.aggregate(avg=Avg("daily_price"))["avg"] or 0,
            })

        context = dict(
            self.admin_site.each_context(request),
            stats=stats,
            title="Host Statistics"
        )
        return TemplateResponse(request, "admin/host_stats.html", context)

    def renter_stats(self, obj):
        if obj.is_host:
            return "-"

        total = Booking.objects.filter(renter=obj).count()
        confirmed = Booking.objects.filter(renter=obj, status='confirmed').count()
        cancelled = Booking.objects.filter(renter=obj, status='cancelled').count()

        return mark_safe(
            f"<b>{total}</b> total<br>"
            f"<span style='color:green;'>{confirmed}</span> confirmed<br>"
            f"<span style='color:red;'>{cancelled}</span> cancelled"
        )

    renter_stats.short_description = "Renter Stats"


admin.site.register(User, UserAdmin)
