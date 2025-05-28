"""
URL configuration for Test_StayFlow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include

from Test_StayFlow import swagger_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.rent.urls')),

    path('api/users/', include('apps.users.urls')),
    path('', include(swagger_urls.urlpatterns)),
    path('api/', include('apps.booking.urls')),
    path("api/payments/", include("apps.payments.urls")),



]
