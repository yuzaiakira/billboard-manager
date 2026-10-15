from functools import update_wrapper

from django.contrib import admin
from django.urls import path

from account.models import UserModel

from addlist import admin_views
from addlist.models import ListsModel


@admin.register(ListsModel)
class ListsModelAdmin(admin.ModelAdmin):
    change_list_template = "template/admin/addlist_listsmodel_changelist.html"
    list_display = ("user", "billboard", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "billboard__name")
    raw_id_fields = ("user", "billboard")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        u = request.user
        extra_context["show_watchlist_users_link"] = u.is_superuser or getattr(u, "user_group", None) == UserModel.ADMIN_USER
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            path(
                "watchlist-users/",
                wrap(admin_views.watchlist_users_list_view),
                name="%s_%s_watchlist_users" % info,
            ),
            path(
                "watchlist-users/<int:user_id>/",
                wrap(admin_views.watchlist_user_detail_view),
                name="%s_%s_watchlist_user_detail" % info,
            ),
        ]
        return custom_urls + super().get_urls()
