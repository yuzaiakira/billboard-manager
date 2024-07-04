from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import admin

from billboard.models import BillboardModel
from billboard.forms import ImportBillboardForm, UpdateBillboardForm


# Create your views here.
class ImportBillboard(PermissionRequiredMixin, FormView):
    model = BillboardModel
    template_name = "template/admin/import-billboard.html"
    permission_required = 'billboard.can_import_billboard'
    form_class = ImportBillboardForm
    success_url = reverse_lazy('admin:billboard_billboardmodel_changelist')

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
            'add': True,
            'change': False
        }

    def form_valid(self, form):
        form.import_from_file(self.request)
        return super().form_valid(form)


class UpdateBillboard(ImportBillboard):
    permission_required = 'billboard.change_billboardmodel'
    form_class = UpdateBillboardForm
