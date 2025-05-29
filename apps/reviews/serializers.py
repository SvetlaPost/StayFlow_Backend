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

        if booking.renter != user:
            raise serializers.ValidationError("You can only rate your own bookings.")
        if booking.end_date > timezone.now().date():
            raise serializers.ValidationError("You can rate only after the rental period ends.")
        if booking.status != "confirmed":
            raise serializers.ValidationError("Only confirmed bookings can be rated.")
        return attrs

    def create(self, validated_data):
        booking = validated_data['booking']
        validated_data['rent'] = booking.rent
        validated_data['renter'] = self.context['request'].user
        return super().create(validated_data)
