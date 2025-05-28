from rest_framework import serializers
from apps.payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "renter",
            "host",
            "rent",
            "total_amount",
            "base_rent",
            "commission_amount",
            "commission_rate",
            "is_paid",
            "paid_at",
            "created_at",
        ]
