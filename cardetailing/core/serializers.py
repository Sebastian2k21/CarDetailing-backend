from django.contrib.auth.models import User
from rest_framework import serializers

from .models import CarService


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ("username", "email", "password", "role")


class ChangePasswordSerializer(serializers.ModelSerializer):
    passwordConfirm = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ("password", "passwordConfirm")


class CarServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarService
        fields = "__all__"
