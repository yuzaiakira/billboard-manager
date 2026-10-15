from django.contrib import admin
from django.urls import reverse

from billboard import models
from billboard.forms import BillboardImageInlineForm
from billboard.widgets import MediaLibraryWidget


class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel
    readonly_fields = ('final_price',)


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    form = BillboardImageInlineForm
    extra = 2

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        media_url = reverse('admin:billboard_billboardmodel_media_library')
        base_form = formset.form

        class FormWithMediaUrl(base_form):
            def __init__(self, *args, **form_kwargs):
                super().__init__(*args, **form_kwargs)
                if 'image' in self.fields:
                    self.fields['image'].widget = MediaLibraryWidget(attrs={
                        'data-media-url': media_url,
                    })

        formset.form = FormWithMediaUrl
        return formset
