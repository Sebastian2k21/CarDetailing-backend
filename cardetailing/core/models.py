from django.contrib.auth.models import User
from djongo import models
import uuid


class CarService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False) #TODO moze lepiej to dac na string? bedzie sie odpowiednio wiazac?
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField()
    detailer = models.ForeignKey(to=User, on_delete=models.PROTECT, related_name="sevices", null=True)

    def __str__(self):
        return f"[{self._id}] {self.name} {self.detailer.username}"


class Role(models.Model):
    id = models.ObjectIdField()
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)


class UserDetails(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    _id = models.ObjectIdField()
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name="role")
    role = models.ForeignKey(to=Role, on_delete=models.PROTECT, related_name="user_roles")


class CarServiceSchedule(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    _id = models.ObjectIdField()
    service = models.ForeignKey(to=CarService, on_delete=models.PROTECT, related_name="schedules")
    day_of_week = models.PositiveIntegerField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.service} | {self.day_of_week} {self.time}"


class CarServiceScheduleSubmit(models.Model):
    class Meta:
        unique_together = ("date", "schedule")

    id = models.UUIDField(default=uuid.uuid4, editable=False)
    _id = models.ObjectIdField()
    date = models.DateTimeField()
    schedule = models.ForeignKey(to=CarServiceSchedule, on_delete=models.PROTECT, related_name="submits")
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, related_name="submits")
