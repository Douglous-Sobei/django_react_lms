from django.urls import path
from api import views as api_views

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user/token/', api_views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('user/register/', api_views.RegisterView.as_view(), name='register-user'),
]
