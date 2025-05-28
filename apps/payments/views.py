from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer

class MyPaymentsView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(renter=self.request.user).select_related("booking", "rent", "host")
