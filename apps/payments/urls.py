from django.urls import path
from apps.payments.views import MyPaymentsView

urlpatterns = [
    path("my/", MyPaymentsView.as_view(), name="my-payments"),
]
