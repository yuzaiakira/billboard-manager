from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ListsModel
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

    def get(self, request):
        self.context['object_list'] = self.model.objects.filter(user=request.user)
        self.context['title'] = "لیست بیلبورد های انتخاب شده"
        # TODO: add only
        return render(request, self.template, self.context)


class PrintPDF(WatchList):
    template = 'template/list/Print_PDF.html'
