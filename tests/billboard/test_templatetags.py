import jdatetime
from django.core.paginator import Paginator
from django.test import SimpleTestCase

from billboard.templatetags.change_bool_value import boolean_value
from billboard.templatetags.jalali_date import jalali_slash
from billboard.templatetags.number_filters import intcomma, normalize_decimal
from billboard.templatetags.paginator_tags import get_proper_elided_page_range


class TemplateTagTests(SimpleTestCase):
    def test_intcomma(self):
        self.assertEqual(intcomma(30000000), '30,000,000')
        self.assertEqual(intcomma(None), '')
        self.assertEqual(intcomma('x'), 'x')

    def test_normalize_decimal(self):
        self.assertEqual(normalize_decimal(5.000), '5')
        self.assertEqual(normalize_decimal(5.500), '5.5')
        self.assertEqual(normalize_decimal(None), '')
        self.assertEqual(normalize_decimal('bad'), 'bad')

    def test_jalali_slash(self):
        self.assertEqual(jalali_slash(None), '')
        self.assertEqual(jalali_slash(jdatetime.date(1404, 3, 1)), '1404/03/01')
        self.assertEqual(jalali_slash('1404-03-01'), '1404/03/01')

    def test_boolean_value(self):
        self.assertEqual(boolean_value(True), 'دارد')
        self.assertEqual(boolean_value(False), 'ندارد')

    def test_elided_page_range(self):
        paginator = Paginator(list(range(100)), 10)
        result = list(get_proper_elided_page_range(paginator, 5, on_each_side=1, on_ends=1))
        self.assertTrue(result)
