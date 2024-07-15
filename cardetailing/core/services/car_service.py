from datetime import datetime

from bson import ObjectId
from rest_framework import status
from rest_framework.generics import get_object_or_404

from core.exceptions import ServiceException
from core.models import CarServiceSchedule, CarServiceScheduleSubmit, CarService


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
