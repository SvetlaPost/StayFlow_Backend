from django.db import models
from drf_yasg import openapi
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    RegisterSerializer,
    BulkRegisterHostSerializer,
    UserProfileSerializer,
)
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrAdmin

User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    @swagger_auto_schema(operation_summary="👤 Get current user profile")
    def get_object(self):
        return self.request.user

class IsSelfOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user and (request.user == obj or request.user.is_staff)

class UserProfileUpdateAPIView(UpdateAPIView):
    permission_classes = [IsSelfOrAdmin]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(operation_summary="✏️ Update current user profile")
    def get_object(self):
        return self.request.user


class PopularHostsAPIView(ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="🔥 List top hosts by number of listings",
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
