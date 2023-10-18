from django.shortcuts import render
from django.db.models import Q

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views import View

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
    slug_field = 'url'
    template_name = "template/home/Billboard_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BillboardDetail, self).get_context_data(*args, **kwargs)
        context['rental_list'] = RentalListModel.get_rental_list(billboard_id=self.object.id)
        return context


class BillboardList(ListView):
    model = BillboardModel
    paginate_by = 12
    template_name = "template/home/Billboard_list.html"


class BillboardCityList(BillboardList):
    def get_queryset(self):
        return self.model.objects.filter(city__url=self.kwargs['slug'])


class BillboardStateList(BillboardList):
    def get_queryset(self):
        return self.model.objects.filter(city__state__url=self.kwargs['slug'])


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
        