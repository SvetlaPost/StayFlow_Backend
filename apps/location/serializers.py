from rest_framework import serializers
from apps.location.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'district', 'state', 'country', 'latitude', 'longitude']
        read_only_fields = ['id']


class LocationWithRentsSerializer(serializers.ModelSerializer):
    rents = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'city', 'district', 'state', 'country', 'latitude', 'longitude', 'rents']

    def get_rents(self, obj):
        from apps.rent.serializers import RentSerializer
        rents = getattr(obj, 'rents_cache', obj.rents.all())
        return RentSerializer(rents, many=True, context=self.context).data

