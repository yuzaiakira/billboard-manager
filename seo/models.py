from django.utils.text import slugify

from django.db import models

# Create your models here.


class SEOBaseModel(models.Model):
    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True, null=True)
    slug = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:  # If instance is new, id is not set yet.
            super(SEOBaseModel, self).save(*args, **kwargs)  # Save to set an ID.
        if not self.slug:
            self.slug = str(self.id)  # Now we can use the ID to set slug.
            super(SEOBaseModel, self).save(*args, **kwargs)  # Save again with slug.
        else:   # Slug exists, just save.
            self.slug = slugify(self.slug, allow_unicode=True)
            super(SEOBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
