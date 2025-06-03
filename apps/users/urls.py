from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from apps.rent.views import RentCreateAPIView
from apps.users.views import (
    RegisterAPIView,
    BulkRegisterHostsAPIView,
    UserMeView,
    UserProfileAPIView,
    UserProfileUpdateAPIView,
    PopularHostsAPIView,
    UserListAPIView,
    MyHostStatsView,
    MyRenterStatsView,
    AdminGroupedBookingsView,
    LogoutAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('bulk-register-hosts/', BulkRegisterHostsAPIView.as_view(), name='bulk_register_hosts'),
    path('all/', UserListAPIView.as_view(), name='user-list'),
    path('me/', UserMeView.as_view(), name='user-me'),
    path("host/my-stats/", MyHostStatsView.as_view(), name="my-host-stats"),
    path('renter/my-stats/', MyRenterStatsView.as_view(), name='my-renter-stats'),
    path("admin/grouped-bookings/", AdminGroupedBookingsView.as_view(), name="admin-grouped-bookings"),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('profile/update/', UserProfileUpdateAPIView.as_view(), name='user-profile-update'),
    path('hosts/popular/', PopularHostsAPIView.as_view(), name='popular-hosts'),

]





