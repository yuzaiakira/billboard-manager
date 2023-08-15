from django.db import models

# source: https://pypi.org/project/django-jalali/
from django_jalali.db import models as jmodels

from adminpanel.models import UserModel

# Create your models here.


class StateModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام استان")

    # SEO Parameter
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    description = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        verbose_name_plural = "استان ها"
        verbose_name = "استان"

    def __str__(self):
        return self.name


class CityModel(models.Model):
    state = models.ForeignKey('StateModel', related_name='CityModel', on_delete=models.CASCADE, verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    # SEO Parameter
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    description = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        verbose_name_plural = "شهر ها"
        verbose_name = "شهر"

    def __str__(self):
        return self.name


class BillboardAttributeModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام ویژگی بیلبورد")

    class Meta:
        verbose_name_plural = "ویژگی های بیلبورد"
        verbose_name = "ویژگی بیلبورد"

    def __str__(self):
        return self.name


class BillboardModel(models.Model):
    city = models.ForeignKey('CityModel', related_name='BillboardModel', on_delete=models.SET_NULL, verbose_name="شهر", null=True)
    name = models.CharField(max_length=100, verbose_name="نام بیلبورد")
    address = models.CharField(max_length=250, verbose_name="محل بیلبورد")
    attribute = models.ManyToManyField(BillboardAttributeModel, verbose_name="ویژگی های بیلبورد")
    description = models.TextField(verbose_name='توضیحات صفحه', blank=True)
    billboard_code = models.CharField(max_length=100, verbose_name="کد بیلبورد", blank=True, null=True)

    has_power = models.BooleanField(verbose_name="برق دارد؟", default=False)
    billboard_length = models.PositiveSmallIntegerField(verbose_name="طول بیلبورد")
    billboard_width = models.PositiveSmallIntegerField(verbose_name="عرض بیلبورد")

    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    reservation_date = jmodels.jDateField(verbose_name="قابل اجاره در", null=True)
    reseller = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name="نماینده", blank=True, null=True)
    latitude = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)

    # SEO Parameter
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    seo_description = models.TextField(max_length=160, verbose_name='توضیحات سئو', blank=True)

    class Meta:
        verbose_name_plural = "بیلبورد ها"
        verbose_name = "بیلبورد"

    def __str__(self):
        return self.name

