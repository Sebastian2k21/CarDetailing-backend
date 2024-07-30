from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CarService, CarServiceSchedule, CarServiceScheduleSubmit, Role, AppUser

# Register your models here.
admin.site.register(CarService)
admin.site.register(CarServiceSchedule)
admin.site.register(CarServiceScheduleSubmit)
admin.site.register(Role)
admin.site.register(AppUser, UserAdmin)
