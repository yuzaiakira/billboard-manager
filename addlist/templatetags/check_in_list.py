from django import template
from addlist.models import ListsModel
register = template.Library()

@register.filter
def on_list(value, user):
    try:
        ListsModel.objects.get(billboard_id=value.id, user= user)
        return True
    except ListsModel.DoesNotExist:
        return False
