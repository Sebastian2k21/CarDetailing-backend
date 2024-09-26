from django.contrib.auth.models import AbstractUser
from djongo import models


class AppUser(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    role_id = models.IntegerField()


class CarService(models.Model):
    id = models.IntegerField()
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField()
    detailer_id = models.IntegerField()
    duration = models.IntegerField(default=0)
    label_color = models.CharField(max_length=10, default="#6aa84f")

    def __str__(self):
        return f"[{self._id}] {self.name} {self.detailer_id}"


class Role(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)


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


class Car(models.Model):
    id = models.IntegerField()
    _id = models.ObjectIdField()
    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year_of_production = models.IntegerField()
    user_id = models.IntegerField()
