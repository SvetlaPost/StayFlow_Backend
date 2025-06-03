from django.urls import path
from apps.location.views import LocationsWithRentsAPIView, LocationCreateAPIView

urlpatterns = [
    path('with-rents/', LocationsWithRentsAPIView.as_view(), name='locations-with-rents'),
    path('create/', LocationCreateAPIView.as_view(), name='location-create'),
]
