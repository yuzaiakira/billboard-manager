from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from billboard.models import BillboardModel
# Create your views here.


class Home(View):
    queryset = BillboardModel.get_recent(9,['name', 'address', 'has_power', 'reservation_date', 'billboard_pic'])

    def get(self, request):
        contex = {
            'queryset': self.queryset
        }
        return render(request, 'template/home/home.html', contex)
