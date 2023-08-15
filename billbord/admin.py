from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
        prepopulated_fields = {'url': ('title',), }
