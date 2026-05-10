from functools import update_wrapper

from openpyxl import Workbook

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect

from account.models import UserModel
from billboard import models, views
from billboard.admin.fieldsets import ADMIN_USER_BILLBOARD_FIELDSETS, DEFAULT_BILLBOARD_FIELDSETS
from billboard.admin.filters import BillboardResellerListFilter
from billboard.admin.inlines import BillboardFinalPriceInline, BillboardImageInline
from siteoption.constants import BILLBOARD_COMMISSION
from siteoption.utils.functions import get_option


def export_billboards_to_xlsx_response(queryset) -> HttpResponse:
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="billboard-list.xlsx"'
    wb = Workbook()
    ws = wb.active
    ws.title = 'billboard list'
    ws.append(['id', 'name', 'price', 'reservation_date'])
    for item in queryset:
        ws.append([str(item.pk), item.name, item.price, str(item.reservation_date)])
    wb.save(response)
    return response


@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    change_list_template = 'template/admin/admin-change-list.html'
    list_display = ('name', 'reseller', 'city', 'reservation_date', 'get_final_price')
    list_filter = (
        'owner_company',
        'city',
        'reservation_date',
        'has_power',
        BillboardResellerListFilter,
    )
    search_fields = ('name', 'address', 'city__name')
    actions = ['make_export', 'assign_to_company', 'assign_to_category']
    prepopulated_fields = {'slug': ('title',)}
    inlines = (BillboardImageInline,)
    raw_id_fields = ('category', 'reseller', 'owner_company')
    fieldsets = DEFAULT_BILLBOARD_FIELDSETS

    def get_commission(self):
        if not hasattr(self, '_commission'):
            self._commission = get_option(BILLBOARD_COMMISSION, 1.2)
        return self._commission

    @admin.display(description='قیمت')
    def get_final_price(self, obj):
        return obj.BillboardFinalPriceModel.final_price

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user
        super().save_model(request, obj, form, change)

    def _sync_final_price_on_create(self, obj):
        final_price_model, created = models.BillboardFinalPriceModel.objects.get_or_create(billboard=obj)
        if obj.reseller.user_group == UserModel.ADMIN_USER:
            final_price = obj.price
        else:
            final_price = (obj.price * self.get_commission()) + obj.BillboardFinalPriceModel.add_price
        final_price_model.final_price = final_price
        if created:
            final_price_model.add_price = obj.BillboardFinalPriceModel.add_price
        final_price_model.save()

    def response_add(self, request, obj, post_url_continue=None):
        self._sync_final_price_on_create(obj)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        models.BillboardFinalPriceModel.update_price(obj, self.get_commission())
        return super().response_change(request, obj)

    def get_fieldsets(self, request, obj=None):
        if not self.fieldsets:
            return [(None, {'fields': self.get_fields(request, obj)})]
        if request.user.user_group == UserModel.ADMIN_USER:
            return ADMIN_USER_BILLBOARD_FIELDSETS
        return self.fieldsets

    def get_inlines(self, request, obj):
        if request.user.user_group != UserModel.ADMIN_USER:
            return super().get_inlines(request, obj)

        default = (BillboardFinalPriceInline, BillboardImageInline)
        try:
            if obj.reseller.user_group == UserModel.ADMIN_USER:
                return (BillboardImageInline,)
        except AttributeError:
            return default
        return default

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
            path('import/', wrap(views.ImportBillboard.as_view()), name='%s_%s_import' % info),
            path('update/', wrap(views.UpdateBillboard.as_view()), name='%s_%s_update' % info),
            path(
                'assign-to-company/',
                self.admin_site.admin_view(views.assign_to_company_view),
                name='%s_%s_assign_to_company' % info,
            ),
            path(
                'assign-to-category/',
                self.admin_site.admin_view(views.assign_to_category_view),
                name='%s_%s_assign_to_category' % info,
            ),
        ]
        return custom_urls + super().get_urls()

    @admin.action(description='خروجی از بیلبورد ها')
    def make_export(self, request, queryset):
        return export_billboards_to_xlsx_response(queryset)

    def assign_to_company(self, request, queryset):
        selected = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        return redirect(f'assign-to-company/?ids={selected}')

    assign_to_company.short_description = 'تعیین شرکت صاحب امتیاز برای بیلبوردهای انتخاب شده'

    def assign_to_category(self, request, queryset):
        selected = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        return redirect(f'assign-to-category/?ids={selected}')

    assign_to_category.short_description = 'انتقال بیلبوردهای انتخاب شده به دسته‌بندی'
