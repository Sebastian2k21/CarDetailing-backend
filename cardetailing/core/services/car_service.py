from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.generics import get_object_or_404
import base64
import uuid

from core.exceptions import ServiceException
from core.models import CarServiceSchedule, CarServiceScheduleSubmit, CarService, Role, AppUser, SubmitStatus, Employee

from core.utils import is_correct_iso_date, get_dates_diff_days

from core.models import Car


class CarServiceManager:
    def get_or_error(self, model_class, object_id: str = None, **kwargs):
        result = model_class.objects
        if object_id:
            result = result.filter(_id=ObjectId(object_id))
        if kwargs:
            result = result.filter(**kwargs)

        result = result.first()
        if not result:
            raise ServiceException(message=f"Object of {model_class} not found",
                                   status_code=status.HTTP_400_BAD_REQUEST)
        return result

    def submit_schedule(self, service_id: str, date: str, user_id: int, car_id: int):
        pending_status = SubmitStatus.objects.filter(name="pending").first()
        if not pending_status:
            raise ServiceException(message="Pending status not exists",
                                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        car_id = ObjectId(car_id)
        service = get_object_or_404(CarService, _id=ObjectId(service_id))
        confirmed_date = datetime.fromisoformat(date)
        if confirmed_date < datetime.now():
            raise ServiceException(message="Date in the past is not allowed", status_code=status.HTTP_400_BAD_REQUEST)

        confirmed_time = confirmed_date.strftime("%H:%M:%S")
        schedule = CarServiceSchedule.objects.filter(service_id=service._id, time=confirmed_time).first()
        if not schedule:
            raise ServiceException(message="Service time not found", status_code=status.HTTP_400_BAD_REQUEST)

        schedule_submit = CarServiceScheduleSubmit.objects.filter(schedule_id=schedule._id, date=confirmed_date).first()
        if schedule_submit:
            raise ServiceException(message="Selected schedule is not available",
                                   status_code=status.HTTP_400_BAD_REQUEST)

        car = Car.objects.filter(_id=car_id).first()
        if not car:
            raise ServiceException(message="Car not found", status_code=status.HTTP_400_BAD_REQUEST)

        CarServiceScheduleSubmit(date=confirmed_date,
                                 schedule_id=schedule._id,
                                 user_id=user_id,
                                 car_id=car_id,
                                 service_id=service_id,
                                 status_id=pending_status._id).save()

    def get_available_schedules(self, service_id: str, date_from: str, date_to: str) -> list[dict[str, str]]:
        service_id = ObjectId(service_id)
        if not is_correct_iso_date(date_from) or not is_correct_iso_date(date_to):
            raise ServiceException(message="Invalid date format, use YYYY-MM-DD",
                                   status_code=status.HTTP_400_BAD_REQUEST)
        if get_dates_diff_days(date_from, date_to) > 31:
            raise ServiceException(message="Date range is too large", status_code=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(CarService, _id=service_id)
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)

        print("66fae8cc11451b11b5895cea" == str(service_id))
        print(service_id)
        dates = []
        while date_from <= date_to:
            schedules = CarServiceSchedule.objects.filter(service_id=str(service_id),
                                                          day_of_week=date_from.weekday() + 1).all()
            if schedules:
                for sh in schedules:
                    submit_exists = False
                    for submit in CarServiceScheduleSubmit.objects.filter(schedule_id=str(sh._id)).all():
                        if submit.date.date() == date_from.date():
                            submit_exists = True
                            break
                    if not submit_exists:
                        service_start_date = datetime(date_from.year, date_from.month, date_from.day, sh.time.hour,
                                                      sh.time.minute, sh.time.second)
                        if service_start_date >= datetime.now():
                            service_end_date = service_start_date + timedelta(minutes=service.duration)
                            dates.append({
                                "text": service_start_date.strftime("%H:%M") + " " + service.name,
                                "start": service_start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                                "end": service_end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                                "backColor": service.label_color
                            })

            date_from += timedelta(days=1)
        return dates

    def get_user_service_submits(self, user_id: int) -> list[dict[str, str | float]]:
        submits = CarServiceScheduleSubmit.objects.filter(user_id=user_id, date__gt=datetime.now()).all()
        result = []
        for sub in submits:
            schedule = CarServiceSchedule.objects.filter(_id=ObjectId(sub.schedule_id)).first()
            service = CarService.objects.filter(_id=ObjectId(schedule.service_id)).first()
            car = Car.objects.filter(_id=ObjectId(sub.car_id)).first()
            result.append({
                "service_id": str(service._id),
                "service_name": service.name,
                "service_price": service.price,
                "service_image": service.image.url,
                "date": sub.date,
                "submit_id": str(sub._id),
                "car_id": sub.car_id,
                "car_name": car.manufacturer + " " + car.model
            })
        return result

    def remove_submit(self, user_id: int, submit_id: str) -> None:
        submit = CarServiceScheduleSubmit.objects.get(_id=ObjectId(submit_id))
        if not submit:
            raise ServiceException(message="Service submit not found", status_code=status.HTTP_400_BAD_REQUEST)
        if str(user_id) != submit.user_id:
            raise ServiceException(message="User is not authorized for this action",
                                   status_code=status.HTTP_403_FORBIDDEN)

        submit.delete()

    def update_submit(self, user_id: int, submit_id: str, new_date: str, car_id: int) -> None:
        if not is_correct_iso_date(new_date):
            raise ServiceException(message="Invalid date format, use YYYY-MM-DD",
                                   status_code=status.HTTP_400_BAD_REQUEST)

        submit = CarServiceScheduleSubmit.objects.get(_id=ObjectId(submit_id))
        if not submit:
            raise ServiceException(message="Service submit not found", status_code=status.HTTP_400_BAD_REQUEST)
        if str(user_id) != submit.user_id:
            raise ServiceException(message="User is not authorized for this action",
                                   status_code=status.HTTP_403_FORBIDDEN)

        new_date = datetime.fromisoformat(new_date)
        exists_submit = CarServiceScheduleSubmit.objects.filter(date=new_date, schedule_id=submit.schedule_id).first()
        if exists_submit:
            raise ServiceException(message="Schedule is not available",
                                   status_code=status.HTTP_403_FORBIDDEN)

        submit.date = new_date
        submit.car_id = car_id
        submit.save()

    def add_service(self, user_id: int, user_role_id: int, service_data: dict[str, Any]):
        user_role_id = ObjectId(user_role_id)
        detailer_role = Role.objects.filter(name="detailer").first()
        if not detailer_role:
            raise ServiceException(message="Detailer role not found, db error",
                                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if detailer_role._id != user_role_id:
            raise ServiceException(message="User has invalid role to add service",
                                   status_code=status.HTTP_400_BAD_REQUEST)

        format, imgstr = service_data["image_file"].split(';base64,')
        ext = format.split('/')[-1]

        image = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.' + ext)

        car_service = CarService(name=service_data["name"],
                                 description=service_data["description"],
                                 duration=service_data["duration"],
                                 price=service_data["price"],
                                 image=image,
                                 detailer_id=user_id)
        car_service.save()

        if "service_days" in service_data:
            for d in service_data["service_days"]:
                CarServiceSchedule(service_id=car_service._id, day_of_week=d["day"], time=d["time"]).save()

    def remove_car(self, user_id: int, car_id: str):
        car = Car.objects.filter(_id=ObjectId(car_id), user_id=str(user_id)).first()
        if not car:
            raise ServiceException(message="Car not found",
                                   status_code=status.HTTP_400_BAD_REQUEST)
        submits = CarServiceScheduleSubmit.objects.filter(car_id=car_id, date__gt=datetime.now())
        if submits:
            raise ServiceException(message="Car is connected with pending services",
                                   status_code=status.HTTP_400_BAD_REQUEST)
        car.is_removed = True
        car.save()

    def get_all_orders(self, detailer_id: int):
        services = list(CarService.objects.filter(detailer_id=detailer_id))
        service_map = {str(service._id): service for service in services}

        schedules = list(CarServiceSchedule.objects.filter(service_id__in=service_map.keys()))
        schedule_map = {str(schedule._id): schedule for schedule in schedules}

        submits = list(CarServiceScheduleSubmit.objects.filter(schedule_id__in=schedule_map.keys()))

        user_ids = {submit.user_id for submit in submits}
        car_ids = {ObjectId(submit.car_id) for submit in submits}
        status_ids = {ObjectId(submit.status_id) for submit in submits}

        users = {user.id: user for user in AppUser.objects.filter(id__in=user_ids)}
        cars = {str(car._id): car for car in Car.objects.filter(_id__in=car_ids)}
        statuses = {str(status._id): status for status in SubmitStatus.objects.filter(_id__in=status_ids)}

        result = []
        for submit in submits:
            client = users.get(int(submit.user_id))
            car = cars.get(submit.car_id)
            schedule = schedule_map.get(submit.schedule_id)
            service = service_map.get(schedule.service_id) if schedule else None
            status = statuses.get(submit.status_id)

            if client and car and schedule and service and status:
                result.append({
                    "id": str(submit._id),
                    "client_id": submit.user_id,
                    "client_phone": client.phone,
                    "client_full_name": client.first_name + " " + client.last_name,
                    "car": car.manufacturer + " " + car.model,
                    "service_name": service.name,
                    "service_id": str(service._id),
                    "service_price": service.price,
                    "due_date": submit.date.strftime("%Y-%m-%d %H:%M"),
                    "status_id": str(status._id),
                    "employee_id": submit.employee_id
                })
        return result

    def remove_employee(self, user_id: int, employee_id: str):
        employee = Employee.objects.filter(_id=ObjectId(employee_id), detailer_id=str(user_id)).first()
        if not employee:
            raise ServiceException(message="Employee not found",
                                   status_code=status.HTTP_400_BAD_REQUEST)
        employee.is_removed = True
        employee.save()

    def attach_employee(self, user_id: int, submit_id: str, employee_id: str):
        submit = self.get_or_error(CarServiceScheduleSubmit, submit_id)
        schedule = self.get_or_error(CarServiceSchedule, submit.schedule_id)
        service = self.get_or_error(CarService, schedule.service_id)

        if service.detailer_id != str(user_id):
            raise ServiceException(message="User has not permission to do this action",
                                   status_code=status.HTTP_403_FORBIDDEN)

        self.get_or_error(Employee, employee_id)
        submit.employee_id = employee_id
        submit.save()

    def set_submit_status(self, user_id: int, submit_id: str, status_id: str):
        submit = self.get_or_error(CarServiceScheduleSubmit, submit_id)
        schedule = self.get_or_error(CarServiceSchedule, submit.schedule_id)
        service = self.get_or_error(CarService, schedule.service_id)

        if service.detailer_id != str(user_id):
            raise ServiceException(message="User has not permission to do this action",
                                   status_code=status.HTTP_403_FORBIDDEN)

        self.get_or_error(SubmitStatus, status_id)

        submit.status_id = status_id
        submit.save()

    def get_detailer_stats(self, detailer_id: int):
        orders = self.get_all_orders(detailer_id)
        pending_status_id = str(self.get_or_error(SubmitStatus, name="pending")._id)
        in_progress_status_id = str(self.get_or_error(SubmitStatus, name="in progress")._id)
        done_status_id = str(self.get_or_error(SubmitStatus, name="done")._id)

        def count_status(status_id: str):
            return len([o for o in orders if o["status_id"] == status_id])

        return {
            "pending_count": count_status(pending_status_id),
            "in_progress_count": count_status(in_progress_status_id),
            "done_count": count_status(done_status_id),
        }
