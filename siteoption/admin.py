from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from siteoption.models import OptionModel
from siteoption.utils.functions import invalidate_option_cache


def validate_value_for_type(value, option_type, key="option"):
    """Validate that value string is valid for the given option type."""
    if option_type == OptionModel.INTEGER:
        try:
            int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer: {value!r}")
    elif option_type == OptionModel.FLOAT:
        try:
            float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid float: {value!r}")
    elif option_type == OptionModel.BOOLEAN:
        raw = (value or "").strip().lower()
        if raw not in ("true", "false", "1", "0", "yes", "no"):
            raise ValidationError(f"Invalid boolean: {value!r}. Use true/false, 1/0, or yes/no.")
    # STRING accepts anything


class OptionModelAdminForm(forms.ModelForm):
    class Meta:
        model = OptionModel
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        value = cleaned.get("value")
        option_type = cleaned.get("type")
        if value is not None and option_type is not None:
            validate_value_for_type(value, option_type, key=cleaned.get("key") or "option")
        return cleaned


@admin.register(OptionModel)
class OptionModelAdmin(admin.ModelAdmin):
    form = OptionModelAdminForm
    list_display = ("key", "type", "value")
    search_fields = ("key",)
    list_editable = ("value",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_option_cache(obj.key)
