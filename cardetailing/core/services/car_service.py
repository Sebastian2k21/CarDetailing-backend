from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.generics import get_object_or_404
import base64
import uuid


from core.exceptions import ServiceException
from core.models import CarServiceSchedule, CarServiceScheduleSubmit, CarService, Role

from core.utils import is_correct_iso_date, get_dates_diff_days


class CarServiceManager:
    def submit_schedule(self, service_id: str, date: str, user_id: int):
        service = get_object_or_404(CarService, _id=ObjectId(service_id))
        confirmed_date = datetime.fromisoformat(date)
        if confirmed_date < datetime.now():
            raise ServiceException(message="Date in the past is not allowed", status_code=status.HTTP_400_BAD_REQUEST)

        confirmed_time = confirmed_date.strftime("%H:%M:%S")
        schedule = CarServiceSchedule.objects.filter(service_id=service.id, time=confirmed_time).first()
        if not schedule:
            raise ServiceException(message="Service time not found", status_code=status.HTTP_400_BAD_REQUEST)

        schedule_submit = CarServiceScheduleSubmit.objects.filter(schedule_id=schedule.id, date=confirmed_date).first()
        if schedule_submit:
            raise ServiceException(message="Selected schedule is not available", status_code=status.HTTP_400_BAD_REQUEST)

        CarServiceScheduleSubmit(date=confirmed_date, schedule_id=schedule.id, user_id=user_id).save()

    def get_available_schedules(self, service_id: str, date_from: str, date_to: str) -> list[dict[str, str]]:
        if not is_correct_iso_date(date_from) or not is_correct_iso_date(date_to):
            raise ServiceException(message="Invalid date format, use YYYY-MM-DD", status_code=status.HTTP_400_BAD_REQUEST)
        if get_dates_diff_days(date_from, date_to) > 31:
            raise ServiceException(message="Date range is too large", status_code=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(CarService, _id=ObjectId(service_id))
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
        return dates

    def get_user_service_submits(self, user_id: int) -> list[dict[str, str | float]]:
        submits = CarServiceScheduleSubmit.objects.filter(user_id=user_id, date__gt=datetime.now()).all()
        result = []
        for sub in submits:
            schedule = CarServiceSchedule.objects.filter(id=sub.schedule_id).first()
            service = CarService.objects.filter(id=schedule.service_id).first()
            result.append({
                "service_id": str(service._id),
                "service_name": service.name,
                "service_price": service.price,
                "service_image": service.image.url ,
                "date": sub.date,
                "submit_id": str(sub._id)
            })
        return result

    def remove_submit(self, user_id: int, submit_id: str) -> None:
        submit = CarServiceScheduleSubmit.objects.get(_id=ObjectId(submit_id))
        if not submit:
            raise ServiceException(message="Service submit not found", status_code=status.HTTP_400_BAD_REQUEST)
        if user_id != submit.user_id:
            raise  ServiceException(message="User is not authorized for this action", status_code=status.HTTP_403_FORBIDDEN)

        submit.delete()

    def update_submit(self, user_id: int, submit_id: str, new_date: str) -> None:
        if not is_correct_iso_date(new_date):
            raise ServiceException(message="Invalid date format, use YYYY-MM-DD", status_code=status.HTTP_400_BAD_REQUEST)

        submit = CarServiceScheduleSubmit.objects.get(_id=ObjectId(submit_id))
        if not submit:
            raise ServiceException(message="Service submit not found", status_code=status.HTTP_400_BAD_REQUEST)
        if user_id != submit.user_id:
            raise  ServiceException(message="User is not authorized for this action", status_code=status.HTTP_403_FORBIDDEN)

        #TODO: dodac zabezpieczenie przed zmiana na zajety termin
        submit.date = datetime.fromisoformat(new_date)
        submit.save()

    def add_service(self, user_id: int, user_role_id: int, service_data: dict[str, Any]):
        detailer_role = Role.objects.filter(name="detailer").first()
        if not detailer_role:
            raise ServiceException(message="Detailer role not found, db error",
                                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if detailer_role.id != user_role_id:
            raise ServiceException(message="User has invalid role to add service", status_code=status.HTTP_400_BAD_REQUEST)

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
                CarServiceSchedule(service_id=car_service.id, day_of_week=d["day"], time=d["time"]).save()
