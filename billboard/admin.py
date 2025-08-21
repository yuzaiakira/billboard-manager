from functools import update_wrapper
from openpyxl import Workbook

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect

from billboard import models, views
from account.models import UserModel

from siteoption.utils.functions import get_option
admin.site.site_header = 'Billboard Manager'
admin.site.index_title = 'ANTEN'


# Register inlines admin class
class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel
    readonly_fields = ('final_price',)


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    extra = 2


# Register models admin class
@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    change_list_template = 'template/admin/admin-change-list.html'
    list_display = ('name', 'reseller', 'city', 'reservation_date', 'get_final_price',)
    list_filter = ('reseller','owner_company', 'city', 'reservation_date', 'billboard_length',
                   'billboard_width', 'has_power')
    search_fields = ('name', 'address', 'city__name')
    actions = ['make_export', 'assign_to_company']
    prepopulated_fields = {'slug': ('title',), }
    inlines = (BillboardImageInline, )
    raw_id_fields = ('category', 'reseller', 'owner_company')
    fieldsets = (("توضیحات بیلبورد",
                  {
                      "fields": ("city", "name", "address", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power",
                                 ("billboard_length", "billboard_width", "price", "reservation_date"),
                                 "category", "owner_company"
                                 ),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "slug", "desc"),
                  }),

                 )

    def get_commission(self):
        if not hasattr(self, '_commission'):
            self._commission = get_option('BillboardCommission', 1.2)

        return self._commission

    def get_final_price(self, obj):
        return obj.BillboardFinalPriceModel.final_price

    get_final_price.short_description = 'قیمت'

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user

        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        final_price_model, created = models.BillboardFinalPriceModel.objects.get_or_create(billboard=obj)
        if obj.reseller.user_group == UserModel.ADMIN_USER:
            final_price = obj.price
        else:
            final_price = (obj.price * self.get_commission()) + obj.BillboardFinalPriceModel.add_price

        if created:
            final_price_model.final_price = final_price
            final_price_model.add_price = obj.BillboardFinalPriceModel.add_price

        else:
            final_price_model.final_price = final_price

        final_price_model.save()

        return super(BillboardAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        models.BillboardFinalPriceModel.update_price(obj, self.get_commission())
        return super(BillboardAdmin, self).response_change(request, obj)

    def get_fieldsets(self, request, obj=None):
        if self.fieldsets:
            if request.user.user_group == UserModel.ADMIN_USER:
                fieldsets = (("توضیحات بیلبورد", {
                      "fields": ("city", "name", "address", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power", "reseller", ("billboard_length", "billboard_width",
                                                           "price", "reservation_date"), "category", "owner_company"),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "slug", "desc"),
                  }),

                 )
                return fieldsets
            else:
                return self.fieldsets
        return [(None, {'fields': self.get_fields(request, obj)})]

    def get_inlines(self, request, obj):
        if request.user.user_group == UserModel.ADMIN_USER:
            new_inlines = (BillboardFinalPriceInline, BillboardImageInline)

            try:
                if obj.reseller.user_group == UserModel.ADMIN_USER:
                    new_inlines = (BillboardImageInline, )

            except AttributeError:
                new_inlines = (BillboardFinalPriceInline, BillboardImageInline)

            return new_inlines

        else:
            return super().get_inlines(request, obj)

    def get_queryset(self, request):
        qs = self.model.objects.by_reseller(request)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_urls(self):
        from django.urls import path
        info = self.opts.app_label, self.opts.model_name

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            path("import/", wrap(views.ImportBillboard.as_view()), name='%s_%s_import' % info),
            path("update/", wrap(views.UpdateBillboard.as_view()), name='%s_%s_update' % info),
            path("assign-to-company/", self.admin_site.admin_view(views.assign_to_company_view), name='assign_to_company'),
        ]

        return custom_urls + super().get_urls()

    @admin.action(description="خروجی از بیلبورد ها")
    def make_export(self, request, queryset) -> HttpResponse:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="billboard-list.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "billboard list"

        # Add headers
        headers = ["id", "name", "price", 'reservation_date']
        ws.append(headers)

        # Add data from the model
        for item in queryset.all():
            ws.append([str(item.id), item.name, item.price, str(item.reservation_date)])

        # Save the workbook to the HttpResponse
        wb.save(response)
        return response


    def assign_to_company(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        return redirect(f'assign-to-company/?ids={",".join(str(pk) for pk in selected)}')

    assign_to_company.short_description = "تعیین شرکت صاحب امتیاز برای بیلبوردهای انتخاب شده"


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }


@admin.display(description="مادر")
def display_parent(obj):
    return obj.parent


@admin.register(models.BillboardCategory)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }
    list_display = ('name', display_parent, 'billboard_visibility')
    search_fields = ('name',)


# Register models
admin.site.register(models.BillboardImageModel)
admin.site.register(models.BillboardFinalPriceModel)