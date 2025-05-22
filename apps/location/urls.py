from django.urls import path
from apps.location.views import LocationsWithRentsAPIView

urlpatterns = [
    path('with-rents/', LocationsWithRentsAPIView.as_view(), name='locations-with-rents'),
]
