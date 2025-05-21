from django.urls import path
from apps.rent.views import (
    RentListAPIView,
    RentCreateAPIView,
    BulkCreateRentAPIView,
    RentRetrieveUpdateDestroyView,

)

urlpatterns = [
    path('rents/', RentListAPIView.as_view(), name='rent-list'),
    path('rents/create/', RentCreateAPIView.as_view(), name='rent-create'),
    path('rents/bulk-create/', BulkCreateRentAPIView.as_view(), name='rent_bulk_create'),

    path('rents/<int:pk>/', RentRetrieveUpdateDestroyView.as_view(), name='rent-detail'),
]



