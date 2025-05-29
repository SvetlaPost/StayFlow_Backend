from django.contrib import admin
from django.urls import path

from apps.payments.admin_views import payment_statistics_view
from apps.payments.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "booking", "renter", "host", "total_amount", 'host_fee_display',
        "commission_amount", "is_paid", "paid_at", "created_at"
    )
    list_filter = ("is_paid", "paid_at", "created_at", "commission_rate")
    search_fields = ("renter__email", "host__email", "rent__title", "booking__id")
    autocomplete_fields = ("renter", "host", "booking", "rent")
    readonly_fields = ("created_at", "paid_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        return qs.filter(renter=request.user) | qs.filter(host=request.user)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("statistics/", self.admin_site.admin_view(payment_statistics_view), name="payment-statistics")
        ]
        return custom_urls + urls

    def host_fee_display(self, obj):
        return obj.base_rent - obj.commission_amount

    host_fee_display.short_description = "Host Fee (calculated)"

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if obj is None:
            return True
        return obj.renter == request.user or obj.host == request.user

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
