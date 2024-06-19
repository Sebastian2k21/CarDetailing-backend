from django.contrib.auth.models import User
from djongo import models


class CarService(models.Model):
    # _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField()


class Role(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)


class UserDetails(models.Model):
    _id = models.ObjectIdField()
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name="role")
    role = models.ForeignKey(to=Role, on_delete=models.PROTECT, related_name="user_roles")
