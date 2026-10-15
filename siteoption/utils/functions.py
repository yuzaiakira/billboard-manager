from django.core.cache import cache

from siteoption.models import OptionModel

CACHE_PREFIX = "siteoption"
CACHE_TIMEOUT = 60


def _cache_key(key):
    return f"{CACHE_PREFIX}:{key}"


def get_option(key, default=None):
    cache_key = _cache_key(key)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        option = OptionModel.objects.get(key=key)
    except OptionModel.DoesNotExist:
        if default is not None:
            return default
        return None
    value = option.clean_value()
    cache.set(cache_key, value, CACHE_TIMEOUT)
    return value


def set_option(key, value, type=None):
    from siteoption.models import OptionModel

    if type is None:
        if isinstance(value, bool):
            type = OptionModel.BOOLEAN
        elif isinstance(value, int):
            type = OptionModel.INTEGER
        elif isinstance(value, float):
            type = OptionModel.FLOAT
        else:
            type = OptionModel.STRING

    if type == OptionModel.BOOLEAN:
        value_str = "True" if value else "False"
    else:
        value_str = str(value)

    OptionModel.objects.update_or_create(
        key=key,
        defaults={"type": type, "value": value_str},
    )
    cache.delete(_cache_key(key))


def invalidate_option_cache(key):
    """Invalidate cached value for an option (e.g. after admin save)."""
    cache.delete(_cache_key(key))
