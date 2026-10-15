from django.utils.text import slugify

from django.db import models


class SEOBaseModel(models.Model):
    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True, null=True)
    slug = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True, null=True)

    def save(self, *args, **kwargs):
        # QuerySet.create() passes force_insert=True; we may save twice (id then slug),
        # so never keep force_insert across both writes.
        kwargs.pop('force_insert', None)

        if not self.pk:
            if not self.slug:
                super().save(*args, **kwargs)
                self.slug = str(self.pk)
                super().save(*args, **kwargs)
                return
            self.slug = slugify(self.slug, allow_unicode=True)
            super().save(*args, **kwargs)
            return

        if not self.slug:
            self.slug = str(self.pk)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
