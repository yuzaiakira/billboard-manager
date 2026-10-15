"""Shared billboard admin fieldset definitions."""

from typing import Tuple


def billboard_fieldsets(*, include_reseller: bool) -> Tuple:
    dim_fields = ('billboard_length', 'billboard_width', 'price', 'reservation_date')
    feature_fields = ('has_power', *dim_fields, 'category', 'owner_company')
    if include_reseller:
        feature_fields = ('has_power', 'reseller', *dim_fields, 'category', 'owner_company')
    return (
        ('توضیحات بیلبورد', {'fields': ('city', 'name', 'address', 'description')}),
        ('ویژگی های بیلورد', {'fields': feature_fields}),
        ('سئو', {'fields': ('billboard_pic', 'map_iframe', 'title', 'slug', 'desc')}),
    )


DEFAULT_BILLBOARD_FIELDSETS = billboard_fieldsets(include_reseller=False)
ADMIN_USER_BILLBOARD_FIELDSETS = billboard_fieldsets(include_reseller=True)
