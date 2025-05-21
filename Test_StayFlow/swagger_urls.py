from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.urls import path, re_path

schema_view = get_schema_view(
    openapi.Info(
        title="StayFlow API",
        default_version='v1',
        description="API for StayFlow housing rental system",
        contact=openapi.Contact(email="svetlana@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
