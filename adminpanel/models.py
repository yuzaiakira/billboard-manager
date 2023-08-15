from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserModel(AbstractUser):

    NORMAL_USER = 0
    RESELLER_USER = 1
    ADMIN_USER = 2

    user_group_status = (
        (NORMAL_USER, 'کاربر ساده'),
        (RESELLER_USER, 'نماینده'),
        (ADMIN_USER, 'ادمین'))

    user_group = models.PositiveSmallIntegerField(choices=user_group_status, verbose_name="نوع کاربر", default=0)
    display_name = models.CharField(max_length=50, verbose_name="نام نمایشی در سایت", blank=True, null=True)
