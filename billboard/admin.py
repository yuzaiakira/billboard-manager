from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.SEOModel)
class SEOAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user
        obj.save()


admin.site.register(models.StateModel)
admin.site.register(models.CityModel)
admin.site.register(models.BillboardAttributeModel)
