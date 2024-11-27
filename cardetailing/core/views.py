from bson import ObjectId
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceException
from .models import CarService, Role, AppUser, CarServiceSchedule, Car, Employee, SubmitStatus
from .permissions import IsDetailer, IsClient
from .serializers import UserCreateSerializer, ChangePasswordSerializer, CarServiceSerializer, \
    SubmitScheduleCreateSerializer, ProfileSerializer, AccountUpdateSerializer, CarServiceScheduleSerializer, \
    CarSerializer, CarAddSerializer, EmployeeAddSerializer, EmployeeSerializer, SubmitStatusSerializer
from .services.car_service import CarServiceManager
from .services.user_service import UserManager

car_service_manager = CarServiceManager()
user_manager = UserManager()


class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serialized = UserCreateSerializer(data=request.data)
        user = AppUser.objects.filter(username=serialized.initial_data['username']).first()
        if user:
            return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        user = AppUser.objects.filter(email=serialized.initial_data['email']).first()
        if user:
            return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.filter(name=serialized.initial_data['role']).first()
        if not role:
            return Response({"message": "Role not found!"}, status=status.HTTP_400_BAD_REQUEST)

        if serialized.is_valid():
            AppUser.objects.create_user(
                username=serialized.initial_data['username'],
                email=serialized.initial_data['email'],
                password=serialized.initial_data['password'],
                role_id=role._id
            )

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


class CarServiceDaysView(ListAPIView):
    serializer_class = CarServiceScheduleSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        service = get_object_or_404(CarService, _id=ObjectId(self.kwargs["pk"]))
        return CarServiceSchedule.objects.filter(service_id=service.id)


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
            car_service_manager.submit_schedule(serializer.initial_data["service_id"],
                                                serializer.initial_data["date"],
                                                request.user.id,
                                                serializer.initial_data["car_id"])
            return Response({"message": "Done"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class UserSubmitsView(APIView):
    def get(self, request):
        try:
            return Response(car_service_manager.get_user_service_submits(request.user.id), status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class UserProfileView(APIView):
    def get(self, request):
        return Response(ProfileSerializer(instance=request.user).data)

    def post(self, request):
        serializer = AccountUpdateSerializer(data=request.data, instance=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Updated"}, status=status.HTTP_200_OK)


class DeleteSubmitScheduleView(APIView):
    def delete(self, request, submit_id: str):
        try:
            car_service_manager.remove_submit(request.user.id, submit_id)
            return Response({"message": "Deleted"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class UpdateSubmitScheduleView(APIView):
    def post(self, request, submit_id: str):
        date = request.data.get("date", "")
        car_id = request.data.get("car_id", None)
        try:
            car_service_manager.update_submit(request.user.id, submit_id, date, car_id)
            return Response({"message": "Updated"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class UserRoleView(APIView):
    def get(self, request):
        try:
            result = user_manager.get_role(request.user)
            return Response(result, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class DetailerServicesListView(ListAPIView):
    serializer_class = CarServiceSerializer

    def get_queryset(self):
        return CarService.objects.filter(detailer_id=self.request.user.id)


class AddServiceView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request):
        try:
            car_service_manager.add_service(request.user.id, request.user.role_id, request.data)
            return Response({"message": "Added"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class CarsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.filter(user_id=self.request.user.id, is_removed=0)


class EmployeesView(ListAPIView):
    permission_classes = [IsAuthenticated, IsDetailer]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(detailer_id=self.request.user.id, is_removed=0)


class AddCarView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request):
        serializer = CarAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["user_id"] = request.user.id
        serializer.save()
        return Response({"message": "Done"}, status=status.HTTP_200_OK)


class AddEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request):
        serializer = EmployeeAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["detailer_id"] = request.user.id
        serializer.save()
        return Response({"message": "Done"}, status=status.HTTP_200_OK)


class RemoveCarView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def delete(self, request, car_id):
        try:
            car_service_manager.remove_car(request.user.id, car_id)
            return Response({"message": "Removed"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class RemoveEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def delete(self, request, employee_id):
        try:
            car_service_manager.remove_employee(request.user.id, employee_id)
            return Response({"message": "Removed"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class OrdersListView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def get(self, request):
        try:
            result = car_service_manager.get_all_orders(self.request.user.id)
            return Response(result, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class AttachEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request, order_id):
        try:
            car_service_manager.attach_employee(request.user.id, order_id, request.data["employee_id"])
            return Response({"message": "Attached"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class SubmitStatusListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsDetailer]
    queryset = SubmitStatus.objects.all()
    serializer_class = SubmitStatusSerializer


class SetSubmitStatusView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request, order_id):
        try:
            car_service_manager.set_submit_status(request.user.id, order_id, request.data["status_id"])
            return Response({"message": "Status set"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class DetailerStatsView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def get(self, request):
        try:
            result = car_service_manager.get_detailer_stats(self.request.user.id)
            return Response(result, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()
