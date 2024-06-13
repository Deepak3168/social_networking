from django.urls import path
from .views import RegisterView,LogoutView,UserSearchView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name="sign_up"),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
]
