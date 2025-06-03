from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView

from apps.location.models import Location
from apps.location.serializers import LocationWithRentsSerializer, LocationSerializer

User = get_user_model()

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        return user

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LocationCreateAPIView(generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAdminUser]


class LocationsWithRentsAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="📍 List locations with filtered rental listings",
        manual_parameters=[
            openapi.Parameter('city', openapi.IN_QUERY, description="City name", type=openapi.TYPE_STRING),
            openapi.Parameter('district', openapi.IN_QUERY, description="District", type=openapi.TYPE_STRING),
            openapi.Parameter('country', openapi.IN_QUERY, description="Country", type=openapi.TYPE_STRING),
            openapi.Parameter('is_active', openapi.IN_QUERY, description="Only active listings", type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get(self, request):
        city = request.query_params.get('city')
        district = request.query_params.get('district')
        country = request.query_params.get('country')
        is_active = request.query_params.get('is_active')

        locations = Location.objects.all()

        if city:
            locations = locations.filter(city__icontains=city)
        if district:
            locations = locations.filter(district__icontains=district)
        if country:
            locations = locations.filter(country__icontains=country)

        locations = locations.prefetch_related('rents')

        for loc in locations:
            rents_qs = loc.rents.all()
            if is_active in ['true', 'True', '1']:
                rents_qs = rents_qs.filter(is_active=True)
            loc.rents_cache = rents_qs

        serializer = LocationWithRentsSerializer(locations, many=True, context={'request': request})
        return Response(serializer.data)
