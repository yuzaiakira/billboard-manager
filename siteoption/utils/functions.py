from siteoption.models import OptionModel


def get_option(key,  default=None):
    try:
        option = OptionModel.objects.get(key=key)

    except OptionModel.DoesNotExist:
        if default is not None:
            return default
        return None

    return option.clean_value()
