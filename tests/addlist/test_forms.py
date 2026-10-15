from django.test import SimpleTestCase

from addlist.forms import ExcelExportFieldForm, PdfExportFieldForm


class ExportFormTests(SimpleTestCase):
    def test_pdf_defaults(self):
        form = PdfExportFieldForm()
        self.assertTrue(form.fields['billboard_pic'].initial)
        self.assertFalse(form.fields['name'].initial)

    def test_excel_binding(self):
        form = ExcelExportFieldForm(data={'city': 'on', 'style': 'on'})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['city'])
