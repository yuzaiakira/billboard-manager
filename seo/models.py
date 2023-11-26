from django.utils.text import slugify

from django.db import models

# Create your models here.


class SEOBaseModel(models.Model):
    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه")
    slug = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Optional
        self.slug = slugify(self.title, allow_unicode=True)
        super(SEOBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
