from django.shortcuts import get_object_or_404
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

from apps.rent.models import Rent
from apps.rent.permissions import IsOwnerOrAdminOrReadOnly
from apps.rent.serializers import RentSerializer, BulkCreateRentSerializer
from apps.rent.filters import RentFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.rent.serializers import RentCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from apps.rent.permissions import IsOwnerOrAdminOrReadOnly
from apps.users.models import User


class RentViewSet(viewsets.ModelViewSet):
    serializer_class = RentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]
    pagination_class = CursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RentFilter
    ordering_fields = ['created_at', 'daily_price', 'monthly_price']
    ordering = ['-created_at']

    def get_queryset(self):
        return Rent.objects.select_related("owner", "location").filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.delete()

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
        permission_classes=[permissions.IsAuthenticated]
    )
    @swagger_auto_schema(
        operation_summary="Restore a soft-deleted listing",
        responses={
            200: openapi.Response(description="Listing restored successfully"),
            400: "Listing is already active",
            403: "Permission denied",
        }
    )
    def restore(self, request, pk=None):
        rent = self.get_object()

        if rent.owner != request.user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if not rent.is_deleted:
            return Response({"detail": "This listing is already active."}, status=status.HTTP_400_BAD_REQUEST)

        rent.is_deleted = False
        rent.save()
        return Response({"detail": "Listing successfully restored."}, status=status.HTTP_200_OK)

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


class RentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RentByUserAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user != user and not request.user.is_staff:
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        rents = Rent.objects.select_related("owner", "location").filter(owner=user, is_deleted=False)
        serializer = RentSerializer(rents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyRentsAPIView(ListAPIView):
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def get_queryset(self):
        return Rent.objects.filter(owner=self.request.user, is_deleted=False).order_by('id')

    @swagger_auto_schema(
        operation_summary="Get current user's rental listings",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filter by active status (true or false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: RentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RentByLocationAPIView(ListAPIView):
    serializer_class = RentSerializer
    permission_classes = [AllowAny]
    pagination_class = RentPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['location__city', 'location__district']
    ordering_fields = ['daily_price', 'monthly_price', 'created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary="Filter listings by city and district",
        manual_parameters=[
            openapi.Parameter('location__city', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="City"),
            openapi.Parameter('location__district', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="District"),
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Sort by fields: daily_price, monthly_price, created_at (prefix with '-' for descending)"),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number"),
        ]
    )

    def get_queryset(self):
        city = self.request.query_params.get('city')
        district = self.request.query_params.get('district')

        queryset = Rent.objects.select_related('location').filter(is_active=True, is_deleted=False)

        if city:
            queryset = queryset.filter(location__city__iexact=city)
        if district:
            queryset = queryset.filter(location__district__iexact=district)

        return queryset