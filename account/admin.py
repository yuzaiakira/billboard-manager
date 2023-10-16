from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.


@admin.register(models.UserModel)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("وضعیت", {'fields': ('user_group', 'display_name')}),
    )


@admin.register(models.BrandModel)
class BillboardAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'user', 'first_name', 'last_name', 'agency', 'phone_number')
    search_fields = ('brand_name', 'first_name', 'last_name', 'agency', 'user', 'id_code', 'phone_number')