from django.shortcuts import render

from api import serializers as api_serializers

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializers.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = api_serializers.User.objects.all()
    serializer_class = api_serializers.RegisterSerializer
    permission_classes = [AllowAny]
