from django import template

register = template.Library()


@register.filter
def jalali_slash(value):
    """
    Format Jalali date as YYYY/MM/DD (e.g. 1404/03/01).
    Accepts jdatetime.date or None; also handles string like '1404-03-01'.
    """
    if value is None:
        return ""
    if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        return f"{value.year}/{value.month:02d}/{value.day:02d}"
    s = str(value).strip()
    if s:
        return s.replace("-", "/")
    return ""
