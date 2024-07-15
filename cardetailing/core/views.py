from bson import ObjectId
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceException
from .models import CarService, UserDetails, Role, CarServiceScheduleSubmit, CarServiceSchedule
from .serializers import UserCreateSerializer, ChangePasswordSerializer, CarServiceSerializer, \
    SubmitScheduleCreateSerializer
from .services.car_service import CarServiceManager
from .utils import is_correct_iso_date, get_dates_diff_days
from datetime import datetime, timedelta

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


class CarServiceAvailableSchedule(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk, date_from, date_to):
        if not is_correct_iso_date(date_from) or not is_correct_iso_date(date_to): #TODO: przeniesc do serwisu
            return Response({"message": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        if get_dates_diff_days(date_from, date_to) > 31:
            return Response({"message": "Date range is too large"}, status=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(CarService, _id=ObjectId(pk))
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)

        dates = []
        while date_from <= date_to:
            schedules = CarServiceSchedule.objects.filter(service_id=service.id, day_of_week=date_from.weekday()+1).all()
            if schedules:
                for sh in schedules:
                    submit_exists = False
                    for submit in CarServiceScheduleSubmit.objects.filter(schedule_id=sh.id).all():
                        if submit.date.date() == date_from.date():
                            submit_exists = True
                            break
                    if not submit_exists:
                        service_start_date = datetime(date_from.year, date_from.month, date_from.day, sh.time.hour, sh.time.minute, sh.time.second)
                        if service_start_date >= datetime.now():
                            service_end_date = service_start_date + timedelta(minutes=service.duration)
                            dates.append({
                                "text": service_start_date.strftime("%H:%M") + " " + service.name,
                                "start": service_start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                                "end": service_end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                                "backColor": service.label_color
                            })

            date_from += timedelta(days=1)
        return Response(dates, status=status.HTTP_200_OK)


class CarServiceSubmitSchedule(APIView):
    def post(self, request):
        serializer = SubmitScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # service = get_object_or_404(CarService, _id=ObjectId(serializer.initial_data["service_id"]))
        # confirmed_date = datetime.fromisoformat(serializer.initial_data["date"])
        # if confirmed_date < datetime.now():
        #     return Response({"message": "Date in the past is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # confirmed_time = confirmed_date.strftime("%H:%M:%S")
        # schedule = CarServiceSchedule.objects.filter(service_id=service.id, time=confirmed_time).first()
        # if not schedule:
        #     return Response({"message": "Service time not found"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # schedule_submit = CarServiceScheduleSubmit.objects.filter(schedule_id=schedule.id, date=confirmed_date).first()
        # if schedule_submit:
        #     return Response({"message": "Selected schedule is not available"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # CarServiceScheduleSubmit(date=confirmed_date, schedule_id=schedule.id, user_id=request.user.id).save()
        # return Response({"message": "Done"}, status=status.HTTP_200_OK)
        try:
            car_service_manager.submit_schedule(serializer.initial_data["service_id"], serializer.initial_data["date"], request.user.id)
            return Response({"message": "Done"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()
