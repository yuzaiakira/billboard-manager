from django.db import models

from account.models import UserModel
from billboard.models import BillboardModel
# Create your models here.


class ListsModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="لیست کاربر", related_name="ListModel")
    billboard = models.ForeignKey(BillboardModel, on_delete=models.CASCADE,
                                  verbose_name="بیلبورد", related_name="ListModel")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.billboard}"
