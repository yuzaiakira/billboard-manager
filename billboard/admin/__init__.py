from django.contrib import admin

from billboard import models

from . import billboards  # noqa: F401 — registers BillboardAdmin

admin.site.site_header = 'Billboard Manager'
admin.site.index_title = 'ANTEN'


@admin.display(description='مادر')
def display_parent(obj):
    return obj.parent


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.BillboardCategory)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('name', display_parent, 'billboard_visibility')
    search_fields = ('name',)


admin.site.register(models.BillboardImageModel)
admin.site.register(models.BillboardFinalPriceModel)
