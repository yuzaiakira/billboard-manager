from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
# Create your views here.


class Home(View):
    quryset = None

    def get(self, request):
        return render(request, 'template/home/home.html')
