from django.db import models

# Create your models here.


class StateModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام استان")

    # SEO Parameter
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    description = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)


class CityModel(models.Model):
    state = models.ForeignKey('StateModel', related_name='state', on_delete=models.CASCADE, verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    # SEO Parameter
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    description = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)
