from django.db import models

# source: https://pypi.org/project/django-jalali/
from django_jalali.db import models as jmodels

from adminpanel.models import UserModel
from .utils import billboard_path

# Create your models here.


class SEOModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    description = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        verbose_name_plural = "محتوا های سئو شده"
        verbose_name = "محتوای سئو شده"

    def __str__(self):
        return self.title


class StateModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام استان")

    seo = models.OneToOneField(SEOModel, on_delete=models.CASCADE, related_name="SEOState",
                               verbose_name="محتوای سئو", blank=True, null=True)

    class Meta:
        verbose_name_plural = "استان ها"
        verbose_name = "استان"

    def __str__(self):
        return self.name


class CityModel(models.Model):
    state = models.ForeignKey('StateModel', related_name='CityModel', on_delete=models.CASCADE, verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    seo = models.OneToOneField(SEOModel, on_delete=models.CASCADE, related_name="SEOCity",
                               verbose_name="محتوای سئو", blank=True, null=True)

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


class BillboardFinalPriceModel(models.Model):
    add_price = models.PositiveBigIntegerField(verbose_name="قیمت افزوده",  default=0, blank=True)
    final_price = models.PositiveBigIntegerField(verbose_name="قیمت نهایی",  default=0, blank=True)

    class Meta:
        verbose_name_plural = "قیمت های نهایی"
        verbose_name = "قیمت نهایی"

    def __str__(self):
        return self.BillboardFinalPrice.name


class BillboardImageModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان عکس", blank=True)
    image = models.ImageField(upload_to=billboard_path, verbose_name="عکس")

    class Meta:
        verbose_name_plural = "عکس های بیلبورد"
        verbose_name = "عکس بیلبورد"

    def __str__(self):
        return self.title


class BillboardModel(models.Model):
    city = models.ForeignKey('CityModel', related_name='BillboardModel', on_delete=models.SET_NULL,
                             verbose_name="شهر", null=True)
    name = models.CharField(max_length=100, verbose_name="نام بیلبورد")
    address = models.CharField(max_length=250, verbose_name="محل بیلبورد")
    attribute = models.ManyToManyField(BillboardAttributeModel, verbose_name="ویژگی های بیلبورد")
    description = models.TextField(verbose_name='توضیحات صفحه', blank=True)

    has_power = models.BooleanField(verbose_name="برق دارد؟", default=False)
    billboard_length = models.PositiveSmallIntegerField(verbose_name="طول بیلبورد")
    billboard_width = models.PositiveSmallIntegerField(verbose_name="عرض بیلبورد")

    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    reservation_date = jmodels.jDateField(verbose_name="قابل اجاره در", null=True)
    reseller = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name="نماینده", blank=True, null=True)

    map_iframe = models.TextField(verbose_name='نقشه', blank=True, null=True)
    billboard_pic = models.ImageField(upload_to=billboard_path, verbose_name="تصویر اصلی بیلبورد",
                                      blank=True, null=True)  # TODO: add location
    billboard_pictures = models.ForeignKey(BillboardImageModel, related_name="BillboardImage",
                                           verbose_name="تصاویر بیلبورد",
                                           on_delete=models.CASCADE, blank=True, null=True)

    final_price = models.OneToOneField(BillboardFinalPriceModel,
                                       related_name='BillboardFinalPrice', verbose_name="قیمت نهایی",
                                       on_delete=models.CASCADE, blank=True, null=True)

    seo = models.OneToOneField(SEOModel, on_delete=models.CASCADE, related_name="SEOBillboard",
                               verbose_name="محتوای سئو", blank=True, null=True)

    class Meta:
        verbose_name_plural = "بیلبورد ها"
        verbose_name = "بیلبورد"

    def __str__(self):
        return self.name
