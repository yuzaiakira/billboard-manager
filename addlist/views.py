from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from openpyxl import Workbook

from .models import ListsModel
from .forms import PdfExportFieldForm, ExcelExportFieldForm
from billboard.utils import billboard_bool_value
# Create your views here.


class AddToList(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, pk):
        item, created = ListsModel.objects.get_or_create(
            user=request.user,
            billboard_id=pk
        )
        item.save()
        return JsonResponse({
            'id': pk,
            'in_list': not created,
            'added': created
        })


class RemoveFromList(AddToList):
    def get(self, request, pk):
        try:
            item = ListsModel.objects.get(user=request.user, billboard_id=pk)
            item.delete()
            deleted = True
        except ListsModel.DoesNotExist:
            deleted = False

        return JsonResponse({
            'id': pk,
            'deleted': deleted
        })


class WatchList(LoginRequiredMixin, View):
    http_method_names = ['get']
    model = ListsModel
    template = 'template/list/Billboard_watch_list.html'
    context = dict()
    context['pdf_form'] = PdfExportFieldForm()
    context['excel_form'] = ExcelExportFieldForm()

    def get(self, request):
        self.context['object_list'] = self.model.objects.filter(user=request.user)
        self.context['title'] = "لیست بیلبورد های انتخاب شده"
        # TODO: add only
        return render(request, self.template, self.context)


class RemoveList(LoginRequiredMixin, View):
    http_method_names = ['get']
    model = ListsModel

    def get(self, request):
        user = request.user
        list_model = self.model.objects.filter(user=user)
        list_model.delete()
        return redirect('WatchList')


class PrintPDF(WatchList):
    template = 'template/list/Print_PDF.html'

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.context['pdf_form'] = PdfExportFieldForm(request.GET)
            if self.context['pdf_form'].is_valid():
                print(self.context['pdf_form'].cleaned_data['billboard_pic'])
                print(self.context['pdf_form'].cleaned_data)

        return super().get(request, *args, **kwargs)


class ExportExcel(LoginRequiredMixin, View):
    model = ListsModel

    # Map ExcelExportFieldForm field names to (excel_header, value_getter key)
    _EXCEL_COLUMNS = {
        'id_code': ('کد بیلبورد', 'id'),
        'city': ('شهر', 'city'),
        'name': ('عنوان بیلبورد', 'name'),
        'address': ('آدرس بیلبورد', 'address'),
        'description': ('توضیحات بیلبورد', 'description'),
        'has_power': ('روشنایی', 'has_power'),
        'size': ('طول', 'billboard_length'),  # size adds two columns
        'size_width': ('عرض', 'billboard_width'),
        'reservation_date': ('تاریخ رزرو', 'reservation_date'),
        'price': ('قیمت بیلبورد', 'price'),
    }

    def get(self, request, *args, **kwargs):
        form = ExcelExportFieldForm(request.GET)
        initial_data = {f: form.fields[f].initial for f in form.fields}
        if form.is_valid():
            data = form.cleaned_data if request.GET else initial_data
            columns = self._build_columns_from_form(data)
        else:
            columns = self._build_columns_from_form(initial_data)
        if not columns:
            columns = self._default_columns()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="billboard-list.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "billboard list"

        headers = [col[0] for col in columns]
        ws.append(headers)

        items = self.model.objects.filter(user=request.user)
        for item in items:
            billboard = item.billboard
            row = []
            for _, key in columns:
                if key == 'id':
                    row.append(str(billboard.id))
                elif key == 'city':
                    row.append(str(billboard.city))
                elif key == 'name':
                    row.append(billboard.name)
                elif key == 'address':
                    row.append(billboard.address)
                elif key == 'description':
                    row.append(billboard.description or '')
                elif key == 'has_power':
                    row.append(billboard_bool_value(billboard.has_power))
                elif key == 'billboard_length':
                    row.append(billboard.billboard_length or '')
                elif key == 'billboard_width':
                    row.append(billboard.billboard_width or '')
                elif key == 'reservation_date':
                    row.append(str(billboard.reservation_date))
                elif key == 'price':
                    row.append(billboard.price or '')
                else:
                    row.append('')
            ws.append(row)

        wb.save(response)
        return response

    def _build_columns_from_form(self, cleaned_data):
        columns = []
        for field_name, (header, key) in self._EXCEL_COLUMNS.items():
            if field_name == 'size_width':
                if cleaned_data.get('size'):
                    columns.append((self._EXCEL_COLUMNS['size_width'][0], self._EXCEL_COLUMNS['size_width'][1]))
                continue
            if cleaned_data.get(field_name):
                columns.append((header, key))
        return columns

    def _default_columns(self):
        """ستون‌های پیش‌فرض وقتی همه فیلدها خاموش باشند (هماهنگ با initial فرم)."""
        return [
            ('کد بیلبورد', 'id'),
            ('شهر', 'city'),
            ('آدرس بیلبورد', 'address'),
            ('توضیحات بیلبورد', 'description'),
            ('روشنایی', 'has_power'),
            ('طول', 'billboard_length'),
            ('عرض', 'billboard_width'),
            ('قیمت بیلبورد', 'price'),
            ('تاریخ رزرو', 'reservation_date'),
        ]
