from django.http import Http404
from django.shortcuts import render
from django.db.models import Q

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views import View
from django.shortcuts import get_object_or_404
from django.utils.encoding import uri_to_iri

from urllib.parse import unquote

from billboard.models import BillboardModel
from billboard.forms import SearchForm
from reservation.models import RentalListModel
# Create your views here.


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
