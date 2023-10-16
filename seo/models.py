from django.db import models

# Create your models here.


class SEOBaseModel(models.Model):
    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        abstract = True