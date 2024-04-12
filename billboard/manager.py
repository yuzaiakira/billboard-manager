from django.db import models
from account.models import UserModel


class BillboardManager(models.Manager):

    def by_reseller(self, request, *args, **kwargs):
        if request.user.user_group == UserModel.ADMIN_USER:
            return super().get_queryset(*args, **kwargs)
        else:
            return super().get_queryset(*args, **kwargs).filter(reseller=request.user)
