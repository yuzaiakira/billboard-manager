from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserModel(AbstractUser):
    user_group_status = (
        (0, 'کاربر ساده'),
        (1, 'نماینده'),
        (2, 'ادمین'))
    user_group = models.PositiveSmallIntegerField(choices=user_group_status, verbose_name="نوع کاربر", default=0)
    display_name = models.CharField(max_length=50, verbose_name="نام نمایشی در سایت", blank=True, null=True)
