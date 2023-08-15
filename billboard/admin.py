from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }
    def save_model(self, request, obj, form, change):
        print(request.user)
        print(request.user)
        print(request.user)
        print(request.user)
        print(request.user)
        if getattr(obj, 'reseller', None) is None:
            obj.reseller = request.user
        obj.save()



admin.site.register(models.BillboardAttributeModel)
