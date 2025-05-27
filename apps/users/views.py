from django.db import models
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, IsAdminUser
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    RegisterSerializer,
    BulkRegisterHostSerializer,
    UserProfileSerializer,
)
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrAdmin, IsSelfOrAdmin
from ..booking.models import Booking
import logging

from ..rent.models import Rent

User = get_user_model()

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)
handler = logging.FileHandler('registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()


            logger.info(f"New user registered: {user.full_name} ({user.email})")


            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }


            logger.info(
                f"New user registered: "
                f"ID={user.id}, Email={user.email}, Full Name={user.full_name}, "
                f"Is Host={user.is_host}, Is Admin={user.is_staff}, Is Active={user.is_active}, "
                f"Refresh Token={tokens['refresh']}, Access Token={tokens['access']}, Role={user.role}"
            )

            welcome_message = f"Welcome to StayFlow, {user.full_name}!"

            # Prepare response
            response_data = serializer.data
            response_data.update({
                'tokens': tokens,
                'message': welcome_message
            })

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"Registration failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BulkRegisterHostsAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=BulkRegisterHostSerializer,
        operation_summary="Register multiple host users"
    )
    def post(self, request):
        serializer = BulkRegisterHostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = serializer.save()
        return Response({"created": [user.email for user in users]}, status=status.HTTP_201_CREATED)


class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    @swagger_auto_schema(operation_summary="Get current user profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update current user profile")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(operation_summary="Get current user profile")
    def get_object(self):
        return self.request.user


class UserProfileUpdateAPIView(UpdateAPIView):
    permission_classes = [IsSelfOrAdmin]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(operation_summary="Update current user profile")
    def get_object(self):
        user = self.request.user
        if not (user.is_staff or self.kwargs.get('pk') == str(user.id)):
            raise PermissionDenied("You can only update your own profile.")
        return user


class PopularHostsAPIView(ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_host', 'is_staff', 'is_active']
    ordering_fields = ['rent_count']

    @swagger_auto_schema(
        operation_summary="List top hosts by number of listings",
        manual_parameters=[
            openapi.Parameter(
                'limit', openapi.IN_QUERY,
                description="Number of top hosts to return",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get_queryset(self):
        limit = self.request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10

        return User.objects.filter(is_host=True)\
            .annotate(rent_count=models.Count('rents'))\
            .order_by('-rent_count')[:limit]


class BookingWithCommissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Calculate and show commission for a booking")
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.select_related('rent').get(pk=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user != booking.renter and not request.user.is_staff:
            raise PermissionDenied("You do not have permission to view this commission.")

        commission = self.calculate_commission(booking)
        return Response({"booking_id": booking.id, "commission": commission}, status=status.HTTP_200_OK)

    def calculate_commission(self, booking):
        total_days = (booking.end_date - booking.start_date).days or 1
        daily_price = booking.rent.daily_price or 0
        return round(total_days * float(daily_price) * 0.1, 2)


class MyHostStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_host:
            raise PermissionDenied("Only hosts can access this endpoint.")

        rents = Rent.objects.filter(owner=user)
        bookings = Booking.objects.filter(rent__in=rents)

        stats = {
            "host_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "total_rents": rents.count(),
            "total_bookings": bookings.count(),
            "confirmed_bookings": bookings.filter(status="confirmed").count(),
            "avg_daily_price": round(rents.aggregate(avg=Avg("daily_price"))["avg"] or 0, 2)
        }

        return Response(stats)

