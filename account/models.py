from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserModel(AbstractUser):

    NORMAL_USER = 0
    MARKETER_USER = 1
    RESELLER_USER = 2
    ADMIN_USER = 3

    user_group_status = (
        (NORMAL_USER, 'کاربر ساده'),
        (MARKETER_USER, 'بازاریاب'),
        (RESELLER_USER, 'نماینده'),
        (ADMIN_USER, 'ادمین'))

    user_group = models.PositiveSmallIntegerField(choices=user_group_status, verbose_name="نوع کاربر", default=0)
    phone_number = models.CharField(max_length=15, verbose_name="شماره تماس", blank=True, null=True)
    display_name = models.CharField(max_length=50, verbose_name="نام نمایشی در سایت", blank=True, null=True)

    company = models.ForeignKey('CompanyModel', verbose_name="شرکت", on_delete=models.SET_NULL,
                                related_name='UserModel', null=True, blank=True)

    @property
    def can_check_reservation(self):
        return self.has_perm("reservation.can_check_reservation")


class BrandModel(models.Model):
    user = models.ForeignKey(UserModel, verbose_name="کاربر", related_name='BrandModel',
                             on_delete=models.SET_NULL, blank=True, null=True)
    brand_name = models.CharField(max_length=255, verbose_name="نام برند", blank=True, null=True)
    id_code = models.CharField(max_length=10, verbose_name="کد ملی", blank=True, null=True)
    first_name = models.CharField(max_length=255, verbose_name="نام", blank=True, null=True)
    last_name = models.CharField(max_length=255, verbose_name="نام خانوادگی", blank=True, null=True)
    phone_number = models.CharField(max_length=15, verbose_name="شماره تماس", blank=True, null=True)
    agency = models.CharField(max_length=355, verbose_name="نمایندگی", blank=True, null=True)
    address = models.TextField(verbose_name="آدرس", blank=True, null=True)
    detail = models.TextField(verbose_name="توضیحات بیشتر", blank=True, null=True)

    class Meta:
        verbose_name_plural = "برند ها"
        verbose_name = "برند"

    def __str__(self):
        if self.brand_name is not None:
            return self.brand_name
        elif self.agency is not None:
            return self.agency

        return "وارد نشده"


class CompanyModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام شرکت")
    address = models.CharField(max_length=255, verbose_name="آدرس شرکت", null=True, blank=True)
    phone = models.CharField(max_length=50, verbose_name="شماره تماس شرکت", null=True, blank=True)
    detail = models.TextField("توضیحات", null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "شرکت ها"
        verbose_name = "شرکت"
