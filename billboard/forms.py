import os
import pandas as pd
from datetime import datetime

from django import forms
from django.conf import settings
import jdatetime

from billboard.models import BillboardModel, CityModel, BillboardFinalPriceModel


class ImportBillboardForm(forms.Form):
    file = forms.FileField(label='فایل')
    city = forms.ChoiceField(choices=[], label="انتخاب شهر")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['file'].widget.attrs[
            'accept'] = ".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet," \
                        " application/vnd.ms-excel"
        self.fields['city'].choices = [(x.pk, x.name) for x in CityModel.objects.all()]

    def import_from_file(self, request):
        base_file = self.make_file()
        dataframe = pd.read_excel(base_file)
        city = CityModel.objects.get(pk=self.cleaned_data["city"])

        for index, row in dataframe.iterrows():

            reservation_date = datetime.strptime(row['reservation_date'], '%Y/%m/%d')
            reservation_date = jdatetime.date(reservation_date.year, reservation_date.month, reservation_date.day)

            billboard = BillboardModel(reseller=request.user,
                                       city=city,
                                       name=row['name'],
                                       address=row['address'],
                                       has_power=row['has_power'],
                                       billboard_length=row['billboard_length'],
                                       billboard_width=row['billboard_width'],
                                       price=row['price'],
                                       reservation_date=reservation_date)
            billboard.save()

            BillboardFinalPriceModel.update_price(billboard, BillboardFinalPriceModel.get_commission())

        # remove file
        os.remove(base_file)

    def make_file(self) -> bytes:
        """
        make file in safe dir wen uploaded
        :return: file address
        """
        file = self.cleaned_data["file"]
        base_file = os.path.join(settings.BASE_DIR, 'tmp/') + file.name
        # create file
        # TODO: check file then created
        with open(base_file, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return base_file
