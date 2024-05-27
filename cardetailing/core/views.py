from django.contrib.auth.models import User
from django.contrib.messages import api
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserCreateSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serialized = UserCreateSerializer(data=request.data)
        if serialized.is_valid():
            user = User.objects.filter(username=serialized.initial_data['username']).first()
            if user:
                return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

            User.objects.create_user(
                username=serialized.initial_data['username'],
                email=serialized.initial_data['email'],
                password=serialized.initial_data['password']
            )
            return Response({"message": "created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

