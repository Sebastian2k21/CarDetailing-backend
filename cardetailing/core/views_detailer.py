from bson import ObjectId
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceException
from .models import CarService, Employee, SubmitStatus
from .permissions import IsDetailer
from .serializers import CarServiceSerializer, \
    EmployeeAddSerializer, EmployeeSerializer, SubmitStatusSerializer
from .services.car_service import CarServiceManager

car_service_manager = CarServiceManager()


class DetailerGetBaseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def get(self, request, **kwargs):
        try:
            return self.get_data(request, **kwargs)
        except ServiceException as e:
            return e.get_response()

    def get_data(self, request, **kwargs):
        return Response({"message": "Operation not implemented"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailerStatsView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        result = car_service_manager.get_detailer_stats(self.request.user.id)
        return Response(result, status=status.HTTP_200_OK)


class DetailerAnalyticsView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        result = car_service_manager.get_analytics(self.request.user.id, kwargs["date_from"], kwargs["date_to"])
        return Response(result, status=status.HTTP_200_OK)


class DetailerClientsView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        result = car_service_manager.get_detailer_clients(self.request.user.id)
        return Response(result, status=status.HTTP_200_OK)


class OrdersListView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        result = car_service_manager.get_all_orders(self.request.user.id)
        return Response(result, status=status.HTTP_200_OK)


class RemoveEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def delete(self, request, employee_id):
        try:
            car_service_manager.remove_employee(request.user.id, employee_id)
            return Response({"message": "Removed"}, status=status.HTTP_200_OK)
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


class AddEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request):
        serializer = EmployeeAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["detailer_id"] = request.user.id
        serializer.save()
        return Response({"message": "Done"}, status=status.HTTP_200_OK)


class EmployeesView(ListAPIView):
    permission_classes = [IsAuthenticated, IsDetailer]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(detailer_id=self.request.user.id, is_removed=0)


class AddServiceView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request):
        try:
            car_service_manager.add_service(request.user.id, request.user.role_id, request.data)
            return Response({"message": "Added"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class DetailerServicesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsDetailer]
    serializer_class = CarServiceSerializer

    def get_queryset(self):
        return CarService.objects.filter(detailer_id=self.request.user.id)
