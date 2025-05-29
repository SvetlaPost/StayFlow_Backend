from decimal import Decimal

from rest_framework import serializers

from apps.location.serializers import LocationSerializer
from apps.rent.models import Rent
from apps.users.serializers import UserProfileSerializer


class RentSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Rent
        fields = [
            'id', 'owner', 'title', 'description', 'location',
            'property_type', 'rooms', 'is_active',
            'is_daily_available', 'daily_price',
            'is_monthly_available', 'monthly_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.is_host:
            raise serializers.ValidationError("Only hosts are allowed to create rental listings.")

        self._validate_price_fields(attrs)
        return attrs

    def _validate_price_fields(self, attrs):
        if attrs.get('is_daily_available'):
            daily_price = attrs.get('daily_price')
            if daily_price is None:
                raise serializers.ValidationError({
                    'daily_price': "Daily price is required if daily rental is enabled."
                })
            if daily_price < 0:
                raise serializers.ValidationError({
                    'daily_price': "Daily price cannot be negative."
                })

        if attrs.get('is_monthly_available'):
            monthly_price = attrs.get('monthly_price')
            if monthly_price is None:
                raise serializers.ValidationError({
                    'monthly_price': "Monthly price is required if monthly rental is enabled."
                })
            if monthly_price < 0:
                raise serializers.ValidationError({
                    'monthly_price': "Monthly price cannot be negative."
                })


class RentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = [
            'title', 'description', 'location', 'property_type', 'rooms',
            'is_active',
            'is_daily_available', 'daily_price',
            'is_monthly_available', 'monthly_price'
        ]

    def validate(self, attrs):
        if attrs.get('is_daily_available'):
            price = attrs.get('daily_price')
            if price is None:
                raise serializers.ValidationError({'daily_price': 'Required for daily rental.'})
            if price <= Decimal("0.00"):
                raise serializers.ValidationError({'daily_price': 'Must be greater than 0.'})
        else:
            attrs['daily_price'] = None

        if attrs.get('is_monthly_available'):
            price = attrs.get('monthly_price')
            if price is None:
                raise serializers.ValidationError({'monthly_price': 'Required for monthly rental.'})
            if price <= Decimal("0.00"):
                raise serializers.ValidationError({'monthly_price': 'Must be greater than 0.'})
        else:
            attrs['monthly_price'] = None

        return attrs


class BulkCreateRentSerializer(serializers.Serializer):
    rents = RentCreateSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        rents_data = validated_data['rents']

        rents = [
            Rent(owner=user, **data)
            for data in rents_data
        ]

        return Rent.objects.bulk_create(rents)

