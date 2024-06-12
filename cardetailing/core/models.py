from djongo import models


class CarService(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField()

