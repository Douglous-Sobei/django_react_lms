from django.shortcuts import render
from api import serializers as api_serializers
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializers.MyTokenObtainPairSerializer
