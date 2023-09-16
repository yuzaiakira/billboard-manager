from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ListsModel
# Create your views here.


class AddToList(LoginRequiredMixin, View):

    def get(self, request, pk):
        item, created = ListsModel.objects.get_or_create(
            user=request.user,
            billboard_id=pk
        )
        item.save()
        return JsonResponse({
            'id':pk,
            'in_list': not created,
            'added': created
        })
