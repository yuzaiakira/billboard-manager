from django.contrib import admin
from reservation import models
# Register your models here.


@admin.register(models.ContractModel)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('brand', 'date', 'name')
    search_fields = ('brand', 'date', 'name')
    prepopulated_fields = {'name': ('date',), }


@admin.register(models.RentalListModel)
class RentalListAdmin(admin.ModelAdmin):
    list_display = ('contract', 'billboard', 'start_date', 'end_date', 'months')
    list_filter = ('start_date', 'end_date')
    search_fields = ('contract', 'billboard', 'start_date', 'end_date')
    raw_id_fields = ('contract', 'billboard')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'billboard_id' in request.GET:
            form.base_fields['billboard'].initial = request.GET['billboard_id']
            form.base_fields['billboard'].widget.attrs['readonly'] = True
        return form
