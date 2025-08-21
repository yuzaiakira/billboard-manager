from django import forms


class ChoseFieldForm(forms.Form):
    billboard_pic = forms.BooleanField(label="عکس بیلبورد", required=False, initial=True)
    id_code = forms.BooleanField(label="کد بیلبورد", required=False)
    name = forms.BooleanField(label="عنوان بیلبورد", required=False, initial=True)
    description = forms.BooleanField(label="توضیحات بیلبورد", required=False)
    address = forms.BooleanField(label="ادرس بیلبورد", required=False, initial=True)
    has_power = forms.BooleanField(label="روشنایی بیلبورد", required=False, initial=True)
    size = forms.BooleanField(label="سایز های بیلبورد", required=False, initial=True)
    reservation_date = forms.BooleanField(label="تاریخ رزرو بیلبورد", required=False, initial=True)
    brand = forms.BooleanField(label="نمایش برند", required=False, initial=True)
    price = forms.BooleanField(label="قیمت بیلبورد", required=False)

