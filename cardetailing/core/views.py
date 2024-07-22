from bson import ObjectId
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceException
from .models import CarService, UserDetails, Role
from .serializers import UserCreateSerializer, ChangePasswordSerializer, CarServiceSerializer, \
    SubmitScheduleCreateSerializer
from .services.car_service import CarServiceManager


car_service_manager = CarServiceManager()


class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serialized = UserCreateSerializer(data=request.data)
        user = User.objects.filter(username=serialized.initial_data['username']).first()
        if user:
            return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=serialized.initial_data['email']).first()
        if user:
            return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.filter(name=serialized.initial_data['role']).first()
        if not role:
            return Response({"message": "Role not found!"}, status=status.HTTP_400_BAD_REQUEST)

        if serialized.is_valid():
            new_user = User.objects.create_user(
                username=serialized.initial_data['username'],
                email=serialized.initial_data['email'],
                password=serialized.initial_data['password']
            )
            UserDetails(user_id=new_user.id, role_id=role.id).save()

            return Response({"message": "created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.initial_data["password"] != serializer.initial_data["passwordConfirm"]:
            return Response({"error": "Password are not the same"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user is None:
            return Response({"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        request.user.set_password(serializer.initial_data["password"])
        request.user.save()
        return Response({"message": "Password changed success"}, status=status.HTTP_200_OK)


class CarServiceListView(ListAPIView):
    serializer_class = CarServiceSerializer
    queryset = CarService.objects.all()
    authentication_classes = []
    permission_classes = []


class CarServiceDetailsView(RetrieveAPIView):
    serializer_class = CarServiceSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        return CarService.objects.filter(_id=ObjectId(self.kwargs["pk"])).first()


class CarServiceAvailableScheduleView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk, date_from, date_to):
        try:
            return Response(car_service_manager.get_available_schedules(pk, date_from, date_to), status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class CarServiceSubmitScheduleView(APIView):
    def post(self, request):
        serializer = SubmitScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            car_service_manager.submit_schedule(serializer.initial_data["service_id"], serializer.initial_data["date"], request.user.id)
            return Response({"message": "Done"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class UserSubmitsView(APIView):
    def get(self, request):
        try:
            return Response(car_service_manager.get_user_service_submits(request.user.id), status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()
