from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import admin, messages
from django.shortcuts import render, redirect

from billboard.models import BillboardModel, CompanyModel
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



def assign_to_company_view(request):
    if request.method == "POST":
        company_id = request.POST.get("company_id")
        ids = request.POST.get("ids", "")
        id_list = ids.split(",")
        BillboardModel.objects.filter(id__in=id_list).update(owner_company_id=company_id)
        messages.success(request, "شرکت صاحب امتیاز با موفقیت اعمال شد.")
        return redirect("/admin/billboard/billboardmodel/")

    ids = request.GET.get("ids", "")
    companies = CompanyModel.objects.all()  # فرض بر اینکه مدل شرکت اینه
    return render(request, "template/admin/assign_to_company.html", {
        "ids": ids,
        "companies": companies,
    })


class UpdateBillboard(ImportBillboard):
    permission_required = 'billboard.change_billboardmodel'
    form_class = UpdateBillboardForm
