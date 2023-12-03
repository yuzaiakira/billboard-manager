from django import template
from addlist.models import ListsModel
register = template.Library()
from django.contrib.auth.models import AnonymousUser


@register.filter
def on_list(value, user):
    if isinstance(user, AnonymousUser):
        # Return False or handle as you see appropriate when user is not authenticated
        return False
    try:
        value.ListModel.get(user=user)
        return True
    except ListsModel.DoesNotExist:
        return False
