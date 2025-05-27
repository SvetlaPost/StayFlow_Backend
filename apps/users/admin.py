from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Avg

from .models import User
from apps.rent.models import Rent
from apps.booking.models import Booking


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Avg

from .models import User
from apps.rent.models import Rent
from apps.booking.models import Booking


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_host', 'is_staff', 'is_active')
    list_filter = ('role',)

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
    ordering = ('email',)

    # 👇 ДОБАВЛЕНО: URL и представление для статистики
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('host-stats/', self.admin_site.admin_view(self.host_stats_view), name="host-stats"),
        ]
        return custom_urls + urls

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


admin.site.register(User, UserAdmin)
