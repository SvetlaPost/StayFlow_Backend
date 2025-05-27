
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from apps.rent.models import Rent
from geopy.distance import distance
from apps.rent.choices.room_type import RoomType



class RentFilter(FilterSet):
    city = filters.CharFilter(field_name='location__city', lookup_expr='iexact')
    district = filters.CharFilter(field_name='location__district', lookup_expr='iexact')
    state = filters.CharFilter(field_name='location__state', lookup_expr='iexact')

    min_daily_price = filters.NumberFilter(field_name='daily_price', lookup_expr='gte')
    max_daily_price = filters.NumberFilter(field_name='daily_price', lookup_expr='lte')

    min_monthly_price = filters.NumberFilter(field_name='monthly_price', lookup_expr='gte')
    max_monthly_price = filters.NumberFilter(field_name='monthly_price', lookup_expr='lte')

    lat = filters.NumberFilter(method='filter_by_radius')
    lng = filters.NumberFilter(method='filter_by_radius')
    radius_km = filters.NumberFilter(method='filter_by_radius')

    property_type = filters.ChoiceFilter(choices=[(rt.name, rt.value) for rt in RoomType])

    class Meta:
        model = Rent
        fields = ['is_active', 'property_type']

    def filter_by_radius(self, queryset, name, value):
        lat = self.data.get('lat')
        lng = self.data.get('lng')
        radius_km = self.data.get('radius_km')

        if lat and lng and radius_km:
            try:
                lat = float(lat)
                lng = float(lng)
                radius_km_val = float(radius_km)

                queryset = queryset.filter(
                    location__latitude__isnull=False,
                    location__longitude__isnull=False
                )

                matched_ids = [
                    rent.id for rent in queryset
                    if distance(
                        (lat, lng),
                        (rent.location.latitude, rent.location.longitude)
                    ).km <= radius_km_val
                ]
                return queryset.filter(id__in=matched_ids)

            except (TypeError, ValueError):
                return queryset.none()

        return queryset