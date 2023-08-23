from django.contrib import admin
from billboard import models
from adminpanel.models import UserModel

# Register inlines admin class
class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    extra = 2


# Register models admin class
@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }
    filter_horizontal = ('attribute',)
    inlines = (BillboardImageInline, )
    fieldsets = (("توضیحات بیلبورد",
                  {
                      "fields": ("city", "name", "address", "attribute", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power", ("billboard_length", "billboard_width", "price", "reservation_date")),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "url", "desc"),
                  }),

                 )

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user


        obj.save()

    def get_fieldsets(self, request, obj=None):
        if self.fieldsets:
            if request.user.user_group == UserModel.ADMIN_USER:
                fieldsets = (("توضیحات بیلبورد",
                  {
                      "fields": ("city", "name", "address", "attribute", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power", "reseller", ("billboard_length", "billboard_width", "price", "reservation_date")),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "url", "desc"),
                  }),

                 )
                return fieldsets
            else:
                return self.fieldsets
        return [(None, {'fields': self.get_fields(request, obj)})]

    def get_inlines(self, request, obj):
        if request.user.user_group == UserModel.ADMIN_USER:
            return (BillboardFinalPriceInline, BillboardImageInline)
        else:
            return super().get_inlines( request, obj)

@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


# Register models
admin.site.register(models.BillboardImageModel)
admin.site.register(models.BillboardFinalPriceModel)
admin.site.register(models.BillboardAttributeModel)
