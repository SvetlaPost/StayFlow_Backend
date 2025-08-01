from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reviews.views import RatingViewSet

router = DefaultRouter()
router.register(r'', RatingViewSet, basename='rating')

urlpatterns = [
    path('', include(router.urls)),
]
