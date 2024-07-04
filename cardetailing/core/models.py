from django.contrib.auth.models import User
from djongo import models


class CarService(models.Model):
    id = models.IntegerField()
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField()
    detailer_id = models.IntegerField()

    def __str__(self):
        return f"[{self._id}] {self.name} {self.detailer_id}"


class Role(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)


class UserDetails(models.Model):
    _id = models.ObjectIdField()
    user_id = models.IntegerField()
    role_id = models.IntegerField()


class CarServiceSchedule(models.Model):
    _id = models.ObjectIdField()
    id = models.IntegerField()
    service_id = models.IntegerField()
    day_of_week = models.PositiveIntegerField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.service_id} | {self.day_of_week} {self.time}"


class CarServiceScheduleSubmit(models.Model):
    class Meta:
        unique_together = ("date", "schedule_id")

    _id = models.ObjectIdField()
    id = models.IntegerField()
    date = models.DateTimeField()
    schedule_id = models.IntegerField()
    user_id = models.IntegerField()
