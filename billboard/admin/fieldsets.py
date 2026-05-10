"""Shared billboard admin fieldset definitions."""

from typing import Tuple


def billboard_fieldsets(*, include_reseller: bool) -> Tuple:
    dims_row = ('billboard_length', 'billboard_width', 'price', 'reservation_date')
    feature_fields = ('has_power', dims_row, 'category', 'owner_company')
    if include_reseller:
        feature_fields = ('has_power', 'reseller', dims_row, 'category', 'owner_company')
    return (
        ('توضیحات بیلبورد', {'fields': ('city', 'name', 'address', 'description')}),
        ('ویژگی های بیلورد', {'fields': feature_fields}),
        ('سئو', {'fields': ('billboard_pic', 'map_iframe', 'title', 'slug', 'desc')}),
    )


DEFAULT_BILLBOARD_FIELDSETS = billboard_fieldsets(include_reseller=False)
ADMIN_USER_BILLBOARD_FIELDSETS = billboard_fieldsets(include_reseller=True)
