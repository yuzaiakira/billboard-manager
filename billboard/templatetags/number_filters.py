from django import template

register = template.Library()


@register.filter
def intcomma(value):
    """
    Format number with thousand separators (every 3 digits).
    e.g. 30000000 -> 30,000,000
    """
    if value is None:
        return ""
    try:
        num = int(float(value))
        return f"{num:,}"
    except (ValueError, TypeError):
        return value
