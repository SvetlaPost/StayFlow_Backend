from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status,generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination, PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, get_object_or_404

from apps.rent.models import Rent
from apps.rent.serializers import RentSerializer, RentCreateSerializer
from apps.rent.filters import RentFilter
from apps.rent.permissions import IsOwnerOrAdminOrReadOnly

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.rent.serializers import BulkCreateRentSerializer
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

    def get_permissions(self):
        if self.action in ['retrieve', 'list', 'popular']:
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly(), IsOwnerOrAdminOrReadOnly()]

    def destroy(self, request, *args, **kwargs):
        print("RENTVIEWSET DESTROY CALLED")
        rent = self.get_object()

        if rent.owner != request.user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if rent.is_deleted:
            return Response({"detail": "This listing is already deleted."}, status=status.HTTP_400_BAD_REQUEST)

        rent.delete()
        rent.save()

        return Response(
            {"detail": f"Listing '{rent.title}' has been successfully marked as deleted."},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="increment-view",
        permission_classes=[permissions.AllowAny]
    )
    def increment_view(self, request, pk=None):
        rent = self.get_object()
        rent.view_count += 1
        rent.save()
        return Response({"message": "View count incremented."}, status=200)

    def get_object(self):
        if self.action == 'restore':
            queryset = Rent.objects.select_related("owner", "location").all()
        else:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.lookup_field)
        try:
            return queryset.get(pk=pk)
        except Rent.DoesNotExist:
            raise NotFound("No Rent matches the given query.")

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=None
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
        try:
            rent = Rent.all_objects.select_related("owner", "location").get(pk=pk)
        except Rent.DoesNotExist:
            return Response({"detail": "No Rent matches the given query."}, status=404)

        if rent.owner != request.user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=403)

        if not rent.is_deleted:
            return Response({"detail": "This listing is already active."}, status=400)

        rent.is_deleted = False
        rent.save()
        return Response({"detail": "Listing successfully restored."}, status=200)

    @action(
        detail=False,
        methods=["get"],
        url_path="popular",
        permission_classes=[AllowAny],
    )
    @swagger_auto_schema(
        operation_summary="Get popular rental listings by views and rating",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Limit number of results (default: 10)"
            )
        ]
    )
    def popular(self, request):
        limit = int(request.query_params.get("limit", 10))
        queryset = self.get_queryset().filter(
            is_active=True
        ).annotate(
            avg_rating=Avg("ratings__stars"),
            calc_ratings_count=Count("ratings")
        ).order_by(
            "-avg_rating", "-view_count"
        )[:limit]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="available-on-weekend",
        permission_classes=[permissions.AllowAny]
    )
    @swagger_auto_schema(
        operation_summary="Get rentals available for weekends",
        operation_description="Returns rentals that are marked as available for daily rental — ideal for weekend stays.",
    )
    def available_on_weekend(self, request):
        queryset = self.get_queryset().filter(
            is_daily_available=True,
            is_active=True,
            is_deleted=False
        ).order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
        user = self.request.user
        if not user.is_host:
            raise PermissionDenied("Only hosts can create rental listings.")

        serializer.save(owner=user)

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


#class RentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#    queryset = Rent.objects.all()
#    serializer_class = RentSerializer
#    permission_classes = [IsOwnerOrAdminOrReadOnly]
#
#    def retrieve(self, request, *args, **kwargs):
#        instance = self.get_object()
#        instance.view_count += 1
#        instance.save()
#        return super().retrieve(request, *args, **kwargs)
#
#    def destroy(self, request, *args, **kwargs):
#        instance = self.get_object()
#
#        if instance.is_deleted:
#            return Response({"detail": "This listing is already deleted."}, status=status.HTTP_400_BAD_REQUEST)
#
#        instance.is_deleted = True
#        instance.save()
#
#        return Response({"detail": "Listing marked as deleted."}, status=status.HTTP_200_OK)


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


