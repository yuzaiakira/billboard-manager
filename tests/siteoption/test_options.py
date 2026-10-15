from django.core.cache import cache
from django.test import RequestFactory, TestCase

from siteoption.admin import OptionModelAdminForm, validate_value_for_type
from siteoption.constants import BILLBOARD_COMMISSION, BILLBOARD_VISIBILITY, SITE_NAME
from siteoption.context_processors import site_options
from siteoption.management.commands.import_data import Command as ImportDataCommand
from siteoption.models import OptionModel
from siteoption.utils.functions import get_option, invalidate_option_cache, set_option


class OptionModelCleanValueTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_clean_value_integer(self):
        opt = OptionModel(key='test_int', type=OptionModel.INTEGER, value='42')
        self.assertEqual(opt.clean_value(), 42)

    def test_clean_value_integer_invalid_raises(self):
        opt = OptionModel(key='test_int_bad', type=OptionModel.INTEGER, value='abc')
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn('Invalid integer', str(ctx.exception))

    def test_clean_value_string(self):
        opt = OptionModel(key='test_str', type=OptionModel.STRING, value='hello')
        self.assertEqual(opt.clean_value(), 'hello')

    def test_clean_value_float(self):
        opt = OptionModel(key='test_float', type=OptionModel.FLOAT, value='1.5')
        self.assertEqual(opt.clean_value(), 1.5)

    def test_clean_value_float_invalid_raises(self):
        opt = OptionModel(key='test_float_bad', type=OptionModel.FLOAT, value='x.y')
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn('Invalid float', str(ctx.exception))

    def test_clean_value_boolean_true(self):
        for val in ('true', 'True', '1', 'yes'):
            opt = OptionModel(key='b', type=OptionModel.BOOLEAN, value=val)
            self.assertIs(opt.clean_value(), True, msg=f'value={val!r}')

    def test_clean_value_boolean_false(self):
        for val in ('false', 'False', '0', 'no'):
            opt = OptionModel(key='b', type=OptionModel.BOOLEAN, value=val)
            self.assertIs(opt.clean_value(), False, msg=f'value={val!r}')

    def test_clean_value_boolean_invalid_raises(self):
        opt = OptionModel(key='test_bool_bad', type=OptionModel.BOOLEAN, value='maybe')
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn('Invalid boolean', str(ctx.exception))

    def test_str(self):
        opt = OptionModel(key='k', type=OptionModel.STRING, value='v')
        self.assertEqual(str(opt), 'k')


class GetOptionTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_get_option_missing_returns_default(self):
        self.assertEqual(get_option('nonexistent_key', default='fallback'), 'fallback')

    def test_get_option_missing_no_default_returns_none(self):
        self.assertIsNone(get_option('nonexistent_key'))

    def test_get_option_integer(self):
        OptionModel.objects.create(key='opt_int', type=OptionModel.INTEGER, value='10')
        self.assertEqual(get_option('opt_int'), 10)

    def test_get_option_string(self):
        OptionModel.objects.create(key='opt_str', type=OptionModel.STRING, value='hello')
        self.assertEqual(get_option('opt_str'), 'hello')

    def test_get_option_float(self):
        OptionModel.objects.create(key='opt_float', type=OptionModel.FLOAT, value='2.5')
        self.assertEqual(get_option('opt_float'), 2.5)

    def test_get_option_boolean(self):
        OptionModel.objects.create(key='opt_bool', type=OptionModel.BOOLEAN, value='True')
        self.assertIs(get_option('opt_bool'), True)

    def test_get_option_uses_cache(self):
        OptionModel.objects.create(key='cached', type=OptionModel.STRING, value='first')
        self.assertEqual(get_option('cached'), 'first')
        OptionModel.objects.filter(key='cached').update(value='second')
        self.assertEqual(get_option('cached'), 'first')


class SetOptionTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_set_option_creates_and_get_returns(self):
        set_option('new_key', 'new_value')
        self.assertEqual(get_option('new_key'), 'new_value')

    def test_set_option_infers_type_bool(self):
        set_option('bool_key', True)
        obj = OptionModel.objects.get(key='bool_key')
        self.assertEqual(obj.type, OptionModel.BOOLEAN)
        self.assertEqual(obj.value, 'True')

    def test_set_option_infers_type_int(self):
        set_option('int_key', 99)
        self.assertEqual(get_option('int_key'), 99)

    def test_set_option_infers_type_float(self):
        set_option('float_key', 1.25)
        self.assertEqual(get_option('float_key'), 1.25)

    def test_set_option_explicit_type(self):
        set_option('typed', '3.14', type=OptionModel.FLOAT)
        obj = OptionModel.objects.get(key='typed')
        self.assertEqual(obj.type, OptionModel.FLOAT)
        self.assertEqual(get_option('typed'), 3.14)

    def test_invalidate_option_cache(self):
        set_option('inv', 'a')
        self.assertEqual(get_option('inv'), 'a')
        OptionModel.objects.filter(key='inv').update(value='b')
        invalidate_option_cache('inv')
        self.assertEqual(get_option('inv'), 'b')


class ImportDataCommandTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_import_data_creates_options_with_expected_keys_and_types(self):
        cmd = ImportDataCommand()
        cmd.handle()
        self.assertTrue(OptionModel.objects.filter(key=SITE_NAME).exists())
        self.assertTrue(OptionModel.objects.filter(key=BILLBOARD_COMMISSION).exists())
        self.assertTrue(OptionModel.objects.filter(key=BILLBOARD_VISIBILITY).exists())
        site_name_opt = OptionModel.objects.get(key=SITE_NAME)
        self.assertEqual(site_name_opt.type, OptionModel.STRING)
        self.assertEqual(site_name_opt.value, 'My Site')

    def test_import_data_is_idempotent(self):
        cmd = ImportDataCommand()
        cmd.handle()
        OptionModel.objects.filter(key=SITE_NAME).update(value='Custom')
        cmd.handle()
        self.assertEqual(OptionModel.objects.get(key=SITE_NAME).value, 'Custom')


class ContextProcessorTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_site_options_default(self):
        request = RequestFactory().get('/')
        ctx = site_options(request)
        self.assertEqual(ctx['site_name'], 'siteName')

    def test_site_options_from_db(self):
        set_option(SITE_NAME, 'Anten')
        request = RequestFactory().get('/')
        ctx = site_options(request)
        self.assertEqual(ctx['site_name'], 'Anten')


class AdminValidationTests(TestCase):
    def test_validate_value_for_type_ok(self):
        validate_value_for_type('10', OptionModel.INTEGER)
        validate_value_for_type('1.5', OptionModel.FLOAT)
        validate_value_for_type('yes', OptionModel.BOOLEAN)
        validate_value_for_type('anything', OptionModel.STRING)

    def test_validate_value_for_type_raises(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_value_for_type('abc', OptionModel.INTEGER)
        with self.assertRaises(ValidationError):
            validate_value_for_type('x', OptionModel.FLOAT)
        with self.assertRaises(ValidationError):
            validate_value_for_type('maybe', OptionModel.BOOLEAN)

    def test_admin_form_clean(self):
        form = OptionModelAdminForm(data={
            'key': 'k1',
            'type': OptionModel.INTEGER,
            'value': 'not-int',
        })
        self.assertFalse(form.is_valid())
