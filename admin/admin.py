from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModel

# Register your models here.


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("وضعیت", {'fields': ('user_group', 'display_name')}),
    )
    list_display = ['username', 'first_name', 'last_name', 'group', 'is_staff']
    list_filter = ['group', 'is_staff']
