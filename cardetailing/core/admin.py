from django.contrib import admin

from .models import CarService, CarServiceSchedule, CarServiceScheduleSubmit, Role, UserDetails

# Register your models here.
admin.site.register(CarService)
admin.site.register(CarServiceSchedule)
admin.site.register(CarServiceScheduleSubmit)
admin.site.register(Role)
admin.site.register(UserDetails)