from urllib.parse import unquote

from django.urls import reverse_lazy
from django.http import Http404

from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from django.contrib import admin, messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.utils.encoding import uri_to_iri

from django.db.models import Q
from billboard.models import BillboardModel, CompanyModel
from billboard.forms import ImportBillboardForm, UpdateBillboardForm, SearchForm
from reservation.models import RentalListModel

    
class Home(View):
    queryset = BillboardModel.get_recent(9)

    def get(self, request):

        context = self.get_context_data()

        return render(request, 'template/home/home.html', context)

    def get_context_data(self, *args, **kwargs):
        context = {
            'queryset': self.queryset,
            'search_form': SearchForm()
        }
        return context


class BillboardDetail(DetailView):
    model = BillboardModel
    slug_field = 'slug'
    template_name = "template/home/Billboard_detail.html"

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.get_slug_field())
        slug = uri_to_iri(slug)
        objects = self.model.objects.filter(slug=slug)

        if not objects.exists():
            raise Http404("No BillboardModel matches the given query.")
        
        # If you want to return the first object or handle multiple objects differently
        return objects.first()  # or handle as needed

    def get_context_data(self, *args, **kwargs):
        context = super(BillboardDetail, self).get_context_data(*args, **kwargs)
        context['rental_list'] = RentalListModel.get_rental_list(billboard_id=self.object.id)
        return context



class BillboardList(ListView):
    model = BillboardModel
    paginate_by = 12
    template_name = "template/home/Billboard_list.html"
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm()
        return context


class BillboardCityList(BillboardList):
    def get(self, request, *args, **kwargs):
        self.kwargs['slug'] = unquote(self.kwargs['slug'])
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(slug=self.kwargs['slug']).order_by('-id')

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj:
            return obj
        else:
            raise Http404("No billboard found")

    def get_queryset(self):
        return self.model.objects.filter(city__slug=self.kwargs['slug']).order_by('-id')


class BillboardStateList(BillboardCityList):
    def get_queryset(self):
        return self.model.objects.filter(city__state__slug=self.kwargs['slug']).order_by('-id')


class BillboardSearch(BillboardList):

    def get_queryset(self):
        query = self.request.GET.get("q")
        cities = self.request.GET.get("cities")
        if query is not None:
            object_list = (self.model.objects.filter(
                Q(name__icontains=query) | Q(city__name__icontains=query) |
                Q(city__state__name__icontains=query) | Q(address__icontains=query)
            ))

            if cities != SearchForm.ALL_CITY:
                object_list = object_list.filter(city__id=cities)

            return object_list.order_by('-id')

        return super().get_queryset()


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
    