from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from openpyxl import Workbook

from .models import ListsModel
from .forms import ChoseFieldForm
from billboard.utils import billboard_bool_value
# Create your views here.


class AddToList(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, pk):
        item, created = ListsModel.objects.get_or_create(
            user=request.user,
            billboard_id=pk
        )
        item.save()
        return JsonResponse({
            'id': pk,
            'in_list': not created,
            'added': created
        })


class RemoveFromList(AddToList):
    def get(self, request, pk):
        try:
            item = ListsModel.objects.get(user=request.user, billboard_id=pk)
            item.delete()
            deleted = True
        except ListsModel.DoesNotExist:
            deleted = False

        return JsonResponse({
            'id': pk,
            'deleted': deleted
        })


class WatchList(LoginRequiredMixin, View):
    http_method_names = ['get']
    model = ListsModel
    template = 'template/list/Billboard_watch_list.html'
    context = dict()
    context['pdf_form'] = ChoseFieldForm()

    def get(self, request):
        self.context['object_list'] = self.model.objects.filter(user=request.user)
        self.context['title'] = "لیست بیلبورد های انتخاب شده"
        # TODO: add only
        return render(request, self.template, self.context)


class RemoveList(LoginRequiredMixin, View):
    http_method_names = ['get']
    model = ListsModel

    def get(self, request):
        user = request.user
        list_model = self.model.objects.filter(user=user)
        list_model.delete()
        return redirect('WatchList')


class PrintPDF(WatchList):
    template = 'template/list/Print_PDF.html'

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.context['pdf_form'] = ChoseFieldForm(request.GET)
            if self.context['pdf_form'].is_valid():
                print(self.context['pdf_form'].cleaned_data['billboard_pic'])
                print(self.context['pdf_form'].cleaned_data)

        return super().get(request, *args, **kwargs)


class ExportExcel(LoginRequiredMixin, View):
    model = ListsModel

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="billboard-list.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "billboard list"

        # Add headers
        headers = ["id", "city", "name", "address", "description", "has_power", "billboard_length", "billboard_width",
                   "price", 'reservation_date']
        ws.append(headers)

        # Add data from the model
        items = self.model.objects.filter(user=self.request.user)
        for item in items:
            billboard = item.billboard
            ws.append([str(billboard.id), str(billboard.city), billboard.name, billboard.address, billboard.description,
                       billboard_bool_value(billboard.has_power), billboard.billboard_length, billboard.billboard_width,
                       billboard.price, str(billboard.reservation_date)])

        # Save the workbook to the HttpResponse
        wb.save(response)
        return response
