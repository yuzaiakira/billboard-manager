from django import forms


class PdfExportFieldForm(forms.Form):
    """PDF export field settings."""
    billboard_pic = forms.BooleanField(label="عکس بیلبورد", required=False, initial=True)
    id_code = forms.BooleanField(label="کد بیلبورد", required=False, initial=True)
    city = forms.BooleanField(label="شهر", required=False, initial=True)
    name = forms.BooleanField(label="عنوان بیلبورد", required=False)
    description = forms.BooleanField(label="توضیحات بیلبورد", required=False)
    address = forms.BooleanField(label="ادرس بیلبورد", required=False, initial=True)
    has_power = forms.BooleanField(label="روشنایی بیلبورد", required=False, initial=True)
    size = forms.BooleanField(label="ابعاد بیلبورد", required=False, initial=True)
    reservation_date = forms.BooleanField(label="تاریخ رزرو بیلبورد", required=False)
    brand = forms.BooleanField(label="نمایش برند", required=False)
    price = forms.BooleanField(label="قیمت بیلبورد", required=False)


class ExcelExportFieldForm(forms.Form):
    """Excel export column settings (without images)."""
    id_code = forms.BooleanField(label="کد بیلبورد", required=False)
    city = forms.BooleanField(label="شهر", required=False, initial=True)
    name = forms.BooleanField(label="عنوان بیلبورد", required=False, initial=False)
    description = forms.BooleanField(label="توضیحات بیلبورد", required=False)
    address = forms.BooleanField(label="ادرس بیلبورد", required=False, initial=True)
    has_power = forms.BooleanField(label="روشنایی بیلبورد", required=False, initial=True)
    size = forms.BooleanField(label="ابعاد بیلبورد", required=False, initial=True)
    reservation_date = forms.BooleanField(label="تاریخ رزرو بیلبورد", required=False, initial=True)
    price = forms.BooleanField(label="قیمت بیلبورد", required=False)
    style = forms.BooleanField(label="ظاهر فارسی", required=False, initial=True)

