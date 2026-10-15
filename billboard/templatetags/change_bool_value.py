from django import template

register = template.Library()


@register.filter
def boolean_value(value):
    return "دارد" if value else "ندارد"