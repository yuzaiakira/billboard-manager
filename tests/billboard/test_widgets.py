from django.test import SimpleTestCase

from billboard.widgets import (
    IntegerStepNumberWidget,
    MediaLibraryWidget,
    ThousandSeparatedNumberWidget,
)


class WidgetTests(SimpleTestCase):
    def test_thousand_format(self):
        w = ThousandSeparatedNumberWidget()
        self.assertEqual(w.format_value(1234567), '1,234,567')
        self.assertEqual(w.format_value(''), '')
        self.assertEqual(w.format_value('abc'), 'abc')

    def test_thousand_parse(self):
        w = ThousandSeparatedNumberWidget()
        self.assertEqual(w.value_from_datadict({'p': '1,234'}, {}, 'p'), '1234')
        self.assertEqual(w.value_from_datadict({'p': '1٬234'}, {}, 'p'), '1234')
        self.assertIsNone(w.value_from_datadict({}, {}, 'p'))

    def test_integer_step_attrs(self):
        w = IntegerStepNumberWidget(attrs={'class': 'extra'})
        self.assertEqual(w.attrs['step'], 'any')
        self.assertIn('integer-step-number', w.attrs['class'])
        self.assertIn('extra', w.attrs['class'])

    def test_media_library_render(self):
        w = MediaLibraryWidget(attrs={'data-media-url': '/admin/media/'})
        html = w.render('billboard_pic', None, attrs={'id': 'id_billboard_pic'})
        self.assertIn('media-library-widget', html)
        self.assertIn('billboard_pic_library_path', html)
        self.assertIn('انتخاب از کتابخانه', html)
