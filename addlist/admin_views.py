from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from django.db.models import Count

from account.models import UserModel
from addlist.models import ListsModel


def _listsmodel_admin_base_context(request):
    return {
        **admin.site.each_context(request),
        "opts": ListsModel._meta,
    }


def _require_admin_watchlist_reports(user):
    if user.is_superuser:
        return
    if getattr(user, "user_group", None) == UserModel.ADMIN_USER:
        return
    raise PermissionDenied


def watchlist_users_list_view(request):
    _require_admin_watchlist_reports(request.user)
    users = (
        UserModel.objects.filter(ListModel__isnull=False)
        .distinct()
        .annotate(watchlist_count=Count("ListModel"))
        .order_by("-watchlist_count", "username")
    )
    return render(
        request,
        "template/admin/watchlist_users_list.html",
        {
            "users": users,
            **_listsmodel_admin_base_context(request),
        },
    )


def watchlist_user_detail_view(request, user_id):
    _require_admin_watchlist_reports(request.user)
    watched_user = get_object_or_404(UserModel, pk=user_id)
    items = (
        ListsModel.objects.filter(user=watched_user)
        .select_related("billboard", "billboard__city")
        .order_by("-created_at")
    )
    return render(
        request,
        "template/admin/watchlist_user_detail.html",
        {
            "watched_user": watched_user,
            "items": items,
            **_listsmodel_admin_base_context(request),
        },
    )
