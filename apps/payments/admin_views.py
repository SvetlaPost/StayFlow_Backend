from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from apps.payments.models import Payment

@staff_member_required
def payment_statistics_view(request):
    total_commission = Payment.objects.filter(is_paid=True).aggregate(Sum("commission_amount"))["commission_amount__sum"] or 0

    by_city = (
        Payment.objects.filter(is_paid=True)
        .values("rent__city")
        .annotate(total_commission=Sum("commission_amount"))
        .order_by("-total_commission")
    )

    context = {
        "total_commission": total_commission,
        "by_city": by_city,
    }
    return render(request, "admin/payment_statistics.html", context)
