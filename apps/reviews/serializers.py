from django.utils import timezone
from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['booking', 'stars', 'comment', 'rent', 'renter']
        read_only_fields = ['rent', 'renter']

    def validate(self, attrs):
        booking = attrs['booking']
        user = self.context['request'].user
        today = timezone.now().date()

        if booking.renter != user:
            raise serializers.ValidationError("You can only rate your own bookings.")
        if today < booking.start_date:
            raise serializers.ValidationError("You can only leave a review starting from the first day of the rental.")
        if booking.status != "confirmed":
            raise serializers.ValidationError("Only confirmed bookings can be rated.")

        return attrs

    def create(self, validated_data):
        booking = validated_data['booking']
        validated_data['rent'] = booking.rent
        validated_data['renter'] = self.context['request'].user
        return super().create(validated_data)

