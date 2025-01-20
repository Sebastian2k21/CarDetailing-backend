from bson import ObjectId
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceException
from .models import CarService, Employee, SubmitStatus, Invoice
from .permissions import IsDetailer
from .serializers import CarServiceSerializer, \
    EmployeeAddSerializer, EmployeeSerializer, SubmitStatusSerializer, InvoiceSerializer
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


class DetailerClientSubmitsView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        result = car_service_manager.get_detailer_client_submits(self.request.user.id, kwargs["client_id"])
        return Response(result, status=status.HTTP_200_OK)


class DetailerInvoiceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def post(self, request):
        try:
            car_service_manager.create_invoice(request.user.id, request.data)
            return Response({"message": "Created"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()


class DetailerInvoiceDownloadView(DetailerGetBaseAPIView):
    def get_data(self, request, **kwargs):
        file, filename = car_service_manager.get_invoice_file(self.request.user.id, kwargs["invoice_id"])
        response = HttpResponse(file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DetailerInvoiceListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsDetailer]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(detailer_id=self.request.user.id)


class RemoveDetailerInvoiceView(APIView):
    permission_classes = [IsAuthenticated, IsDetailer]

    def delete(self, request, invoice_id):
        try:
            car_service_manager.remove_invoice(request.user.id, invoice_id)
            return Response({"message": "Removed"}, status=status.HTTP_200_OK)
        except ServiceException as e:
            return e.get_response()
