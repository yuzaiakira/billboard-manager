from django.contrib import admin

from billboard import models


class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel
    readonly_fields = ('final_price',)


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    extra = 2
