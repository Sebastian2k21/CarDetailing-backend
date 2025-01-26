from rest_framework import serializers

from .models import CarService, AppUser, CarServiceSchedule, Car, Employee, SubmitStatus, Invoice


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=50)

    class Meta:
        model = AppUser
        fields = ("username", "email", "password", "role")


class ChangePasswordSerializer(serializers.ModelSerializer):
    passwordConfirm = serializers.CharField(max_length=50)

    class Meta:
        model = AppUser
        fields = ("password", "passwordConfirm")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ["id", "username"]


class CarServiceSerializer(serializers.ModelSerializer):
    detailer = serializers.SerializerMethodField()

    def get_detailer(self, obj):
        return UserSerializer(AppUser.objects.filter(id=obj.detailer_id).first()).data

    class Meta:
        model = CarService
        fields = "__all__"


class CarServiceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarServiceSchedule
        fields = "__all__"


class SubmitScheduleCreateSerializer(serializers.Serializer):
    service_id = serializers.CharField(max_length=30)
    date = serializers.DateTimeField()


class ProfileSerializer(serializers.ModelSerializer):
    # company_name = serializers.CharField(max_length=200, required=False)
    # nip = serializers.CharField(max_length=11, required=False)

    class Meta:
        model = AppUser
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "street", "city", "zip_code", "nip", "company_name"]


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ["email", "first_name", "last_name",  "phone", "street", "city", "zip_code", "nip", "company_name"]


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ["_id", "manufacturer", "model", "year_of_production"]


class CarAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ["manufacturer", "model", "year_of_production"]


class EmployeeAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "description", "experience"]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["_id", "first_name", "last_name", "description", "experience"]


class SubmitStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitStatus
        fields = ["_id", "name"]


class InvoiceSerializer(serializers.ModelSerializer):
    number = serializers.SerializerMethodField()

    def get_number(self, obj):
        return f"FV/{obj.date_created.strftime('%Y')}/{obj.number:04}"

    class Meta:
        model = Invoice
        fields = ["_id", "date_created", "first_name", "last_name", "amount_brutto", "number"]
