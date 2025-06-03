from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.rent.views import (
    RentViewSet,
    RentByUserAPIView,
    MyRentsAPIView,
    RentByLocationAPIView, RentCreateAPIView,
)

router = DefaultRouter()
router.register(r'', RentViewSet, basename='rent')

urlpatterns = [
    path('my/', MyRentsAPIView.as_view(), name='my-rents'),
    path('by-user/<int:user_id>/', RentByUserAPIView.as_view(), name='rents-by-user'),
    path('by-location/', RentByLocationAPIView.as_view(), name='rents-by-location'),
    path('create/', RentCreateAPIView.as_view(), name='rent-create'),
    path('', include(router.urls)),

]




