from django.contrib import admin

from account.models import UserModel
from billboard import models


class BillboardResellerListFilter(admin.SimpleListFilter):
    """Only users who appear as reseller on at least one visible billboard (not every User row)."""

    title = models.BillboardModel._meta.get_field('reseller').verbose_name
    parameter_name = 'reseller'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.by_reseller(request).exclude(reseller__isnull=True)
        reseller_ids = qs.values_list('reseller_id', flat=True).distinct()
        users = UserModel.objects.filter(pk__in=reseller_ids).order_by('username')
        return [(str(u.pk), str(u)) for u in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reseller_id=self.value())
        return queryset
