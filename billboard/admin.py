from django.contrib import admin
from billboard import models


# Register inlines admin class
class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    extra = 2


# Register models admin class
@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }
    filter_horizontal = ('attribute',)
    inlines = (BillboardFinalPriceInline, BillboardImageInline)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user
        obj.save()


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


# Register models
admin.site.register(models.BillboardImageModel)
admin.site.register(models.BillboardFinalPriceModel)
admin.site.register(models.BillboardAttributeModel)
