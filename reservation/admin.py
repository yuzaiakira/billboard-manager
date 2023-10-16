from django.contrib import admin
from reservation import models
# Register your models here.


@admin.register(models.ContractModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ('brand', 'date', 'name')
    search_fields = ('brand', 'date', 'name')
    prepopulated_fields = {'name': ('date',), }


@admin.register(models.RentalListModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ('contract', 'billboard', 'start_date', 'end_date', 'months')
    list_filter = ('start_date', 'end_date')
    search_fields = ('contract', 'billboard', 'start_date', 'end_date')
