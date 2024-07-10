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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CarServiceSerializer(serializers.ModelSerializer):
    detailer = serializers.SerializerMethodField()

    def get_detailer(self, obj):
        return UserSerializer(User.objects.filter(id=obj.detailer_id).first()).data

    class Meta:
        model = CarService
        fields = "__all__"


class SubmitScheduleCreateSerializer(serializers.Serializer):
    service_id = serializers.CharField(max_length=30)
    date = serializers.DateTimeField()

    def save(self, **kwargs):
        print("OK")
