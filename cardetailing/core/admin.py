from django.contrib import admin

from .models import CarService, CarServiceSchedule, CarServiceScheduleSubmit

# Register your models here.
admin.site.register(CarService)
admin.site.register(CarServiceSchedule)
admin.site.register(CarServiceScheduleSubmit)