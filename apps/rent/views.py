from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.rent.models import Rent
from apps.rent.permissions import IsOwnerOrAdminOrReadOnly
from apps.rent.serializers import RentSerializer, BulkCreateRentSerializer
from apps.rent.filters import RentFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.rent.serializers import RentCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions


class RentListAPIView(generics.ListAPIView):
    queryset = Rent.objects.filter(is_active=True, is_deleted=False)
    serializer_class = RentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RentFilter

    @swagger_auto_schema(
        operation_summary="List active rental listings",
        operation_description="""
            Returns a list of active rental properties.
            You can filter results by:
            - city, district, state
            - daily/monthly price range
            - location radius (via lat, lng, radius_km)
        """,
        manual_parameters=[
            openapi.Parameter('city', openapi.IN_QUERY, description="City name", type=openapi.TYPE_STRING),
            openapi.Parameter('district', openapi.IN_QUERY, description="District name", type=openapi.TYPE_STRING),
            openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude (for radius search)", type=openapi.TYPE_NUMBER),
            openapi.Parameter('lng', openapi.IN_QUERY, description="Longitude (for radius search)", type=openapi.TYPE_NUMBER),
            openapi.Parameter('radius_km', openapi.IN_QUERY, description="Radius in kilometers", type=openapi.TYPE_NUMBER),
            openapi.Parameter('min_daily_price', openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_daily_price', openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RentCreateAPIView(generics.CreateAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentCreateSerializer
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_summary="Create a rental listing",
        operation_description="Create a new property listing for rent.",
        responses={201: RentCreateSerializer()},
        request_body=RentCreateSerializer
    )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BulkCreateRentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=BulkCreateRentSerializer)
    def post(self, request):
        serializer = BulkCreateRentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        rents = serializer.save()
        return Response({"created": len(rents)}, status=status.HTTP_201_CREATED)


class RentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
