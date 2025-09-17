from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from userauths.models import Profile, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include additional user information in the JWT token.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
