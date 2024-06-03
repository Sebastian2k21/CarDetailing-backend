from django.contrib.auth.models import User
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")


class ChangePasswordSerializer(serializers.ModelSerializer):
    passwordConfirm = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ("password", "passwordConfirm")
