import random
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from api import serializers as api_serializer
from userauths.models import Profile

User = get_user_model()

# -------------------------
# JWT Login View
# -------------------------


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Returns JWT tokens and user info on login.
    """
    serializer_class = api_serializer.MyTokenObtainPairSerializer


# -------------------------
# Registration View
# -------------------------
class RegisterView(generics.CreateAPIView):
    """
    Handles new user registration.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer


# -------------------------
# OTP Generator
# -------------------------
def generate_random_otp(length=6):
    """
    Generates a numeric OTP of given length.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


# -------------------------
# Password Reset Email Verification View
# -------------------------
class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    """
    Verifies email and generates:
    - OTP
    - Refresh token
    - Reset link with query params
    """
    permission_classes = [AllowAny]
    # Optional: used if you want to serialize user
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            raise api_serializer.serializers.ValidationError(
                {"email": "User with this email does not exist."})

        # Generate refresh token and OTP
        refresh = RefreshToken.for_user(user)
        user.refresh_token = str(refresh.access_token)
        user.otp = generate_random_otp()
        user.save()

        # Construct reset link
        reset_link = (
            f"http://localhost:5173/create-new-password/"
            f"?otp={user.otp}&uuidb64={user.pk}&refresh_token={user.refresh_token}"
        )

        return {
            "email": user.email,
            "username": user.username,
            "reset_link": reset_link
        }

    def retrieve(self, request, *args, **kwargs):
        context = self.get_object()
        return Response(context)
