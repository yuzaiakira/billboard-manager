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


@register.filter
def normalize_decimal(value):
    """
    Remove trailing zeros from decimal numbers.
    e.g. 5.000 -> 5, 5.500 -> 5.5, 5.123 -> 5.123
    """
    if value is None:
        return ""
    try:
        num = float(value)
        # Convert to string and remove trailing zeros
        if num == int(num):
            return str(int(num))
        return str(num).rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return value
