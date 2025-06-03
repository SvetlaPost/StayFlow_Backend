from django.contrib import admin
from django.urls import path, include
from Test_StayFlow import swagger_urls

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/rents/', include('apps.rent.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/bookings/', include('apps.booking.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/locations/', include('apps.location.urls')),

    path('api/reviews/', include('apps.reviews.urls')),


    # Swagger
    path('', include(swagger_urls.urlpatterns)),
]
