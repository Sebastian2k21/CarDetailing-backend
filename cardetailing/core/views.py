from bson import ObjectId
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CarService, UserDetails, Role
from .serializers import UserCreateSerializer, ChangePasswordSerializer, CarServiceSerializer
from .utils import is_correct_iso_date, get_dates_diff_days
from datetime import datetime, timedelta


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

        if serialized.is_valid():
            new_user = User.objects.create_user(
                username=serialized.initial_data['username'],
                email=serialized.initial_data['email'],
                password=serialized.initial_data['password']
            )
            role = get_object_or_404(Role, name=serialized.initial_data['role'])
            UserDetails(user=new_user, role=role).save()

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


class CarServiceAvailableSchedule(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk, date_from, date_to):
        if not is_correct_iso_date(date_from) or not is_correct_iso_date(date_to):
            return Response({"message": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        if get_dates_diff_days(date_from, date_to) > 31:
            return Response({"message": "Date range is too large"}, status=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(CarService, _id=ObjectId(pk))
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)

        result = {}
        while date_from <= date_to:
            schedules = service.schedules.filter(day_of_week=date_from.weekday()+1).all()
            available_time = list()
            result[date_from.strftime("%Y-%m-%d")] = available_time
            if schedules:
                for sh in schedules:
                    submit_exists = False
                    for submit in sh.submits.all():
                        if submit.date.date() == date_from.date():
                            submit_exists = True
                            break
                    if not submit_exists:
                        available_time.append(str(sh.time))

            date_from += timedelta(days=1)
        return Response(result, status=status.HTTP_200_OK)
