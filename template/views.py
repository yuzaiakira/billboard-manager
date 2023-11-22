from django.http import Http404
from django.shortcuts import render
from django.db.models import Q

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views import View

from urllib.parse import unquote

from billboard.models import BillboardModel
from reservation.models import RentalListModel
# Create your views here.


class Home(View):
    queryset = BillboardModel.get_recent(9)

    def get(self, request):
        contex = {
            'queryset': self.queryset
        }
        return render(request, 'template/home/home.html', contex)


class BillboardDetail(DetailView):
    model = BillboardModel
    slug_field = 'slug'
    template_name = "template/home/Billboard_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BillboardDetail, self).get_context_data(*args, **kwargs)
        context['rental_list'] = RentalListModel.get_rental_list(billboard_id=self.object.id)
        return context


class BillboardList(ListView):
    model = BillboardModel
    paginate_by = 12
    template_name = "template/home/Billboard_list.html"
    slug_url_kwarg = 'slug'




class BillboardCityList(BillboardList):
    def get(self, request, *args, **kwargs):
        self.kwargs['slug'] = unquote(self.kwargs['slug'])
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(slug=self.kwargs['slug'])

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj:
            return obj
        else:
            raise Http404("No billboard found")

    def get_queryset(self):
        return self.model.objects.filter(city__slug=self.kwargs['slug'])
        # return self.model.objects.filter(city__id=self.kwargs['pk'])


class BillboardStateList(BillboardCityList):
    def get_queryset(self):
        return self.model.objects.filter(city__state__slug=self.kwargs['slug'])


class BillboardSearch(BillboardList):

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query is not None:
            object_list = self.model.objects.filter(
                Q(name__icontains=query) | Q(city__name__icontains=query) | Q(city__state__name__icontains=query) |
                Q(address__icontains=query)
            )
            return object_list
        return super().get_queryset()
