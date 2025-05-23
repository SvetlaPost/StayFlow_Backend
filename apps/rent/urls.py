from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.rent.views import (
    RentViewSet,
    RentByUserAPIView,
    MyRentsAPIView,
    RentByLocationAPIView,
)

router = DefaultRouter()
router.register(r'rents', RentViewSet, basename='rent')

urlpatterns = [
    path('rents/my/', MyRentsAPIView.as_view(), name='my-rents'),
    path('rents/by-user/<int:user_id>/', RentByUserAPIView.as_view(), name='rents-by-user'),
    path('rents/by-location/', RentByLocationAPIView.as_view(), name='rents-by-location'),  # 👈 новый путь
    path('', include(router.urls)),
]



