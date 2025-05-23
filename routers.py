from django.contrib import admin
from django.urls import path, include

from Test_StayFlow import swagger_urls

urlpatterns = [

    path('api/', include('apps.rent.urls')),

    path('api/, include('apps..urls')),
    path('', include(swagger_urls.urlpatterns)),

]