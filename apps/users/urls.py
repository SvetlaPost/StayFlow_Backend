from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,

)

from apps.users.views import (
    RegisterAPIView,
    BulkRegisterHostsAPIView,
    UserMeView, UserProfileAPIView, UserProfileUpdateAPIView, PopularHostsAPIView, UserListAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('bulk-register-hosts/', BulkRegisterHostsAPIView.as_view(), name='bulk_register_hosts'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('all/', UserListAPIView.as_view(), name='user-list'),
    path('me/', UserMeView.as_view(), name='user-me'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('profile/update/', UserProfileUpdateAPIView.as_view(), name='user-profile-update'),
    path('hosts/popular/', PopularHostsAPIView.as_view(), name='popular-hosts'),

]




