from rest_framework import serializers
from apps.booking.models import Booking
from datetime import date

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['renter', 'commission_amount', 'created_at', 'updated_at']

    def validate(self, attrs):
        rent = attrs['rent']
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")

        # Проверка на пересекающиеся брони
        overlapping_bookings = Booking.objects.filter(
            rent=rent,
            status='confirmed',
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError("This property is already booked for the selected dates.")

        return attrs
