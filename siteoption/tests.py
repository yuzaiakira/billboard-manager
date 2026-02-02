from django.core.cache import cache
from django.test import TestCase

from siteoption.constants import BILLBOARD_COMMISSION, BILLBOARD_VISIBILITY, SITE_NAME
from siteoption.management.commands.import_data import Command as ImportDataCommand
from siteoption.models import OptionModel
from siteoption.utils.functions import get_option, set_option


class OptionModelCleanValueTests(TestCase):
    """Tests for OptionModel.clean_value() per type."""

    def setUp(self):
        cache.clear()

    def test_clean_value_integer(self):
        opt = OptionModel(key="test_int", type=OptionModel.INTEGER, value="42")
        self.assertEqual(opt.clean_value(), 42)

    def test_clean_value_integer_invalid_raises(self):
        opt = OptionModel(key="test_int_bad", type=OptionModel.INTEGER, value="abc")
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn("Invalid integer", str(ctx.exception))

    def test_clean_value_string(self):
        opt = OptionModel(key="test_str", type=OptionModel.STRING, value="hello")
        self.assertEqual(opt.clean_value(), "hello")

    def test_clean_value_float(self):
        opt = OptionModel(key="test_float", type=OptionModel.FLOAT, value="1.5")
        self.assertEqual(opt.clean_value(), 1.5)

    def test_clean_value_float_invalid_raises(self):
        opt = OptionModel(key="test_float_bad", type=OptionModel.FLOAT, value="x.y")
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn("Invalid float", str(ctx.exception))

    def test_clean_value_boolean_true(self):
        for val in ("true", "True", "1", "yes"):
            opt = OptionModel(key="b", type=OptionModel.BOOLEAN, value=val)
            self.assertIs(opt.clean_value(), True, msg=f"value={val!r}")

    def test_clean_value_boolean_false(self):
        for val in ("false", "False", "0", "no"):
            opt = OptionModel(key="b", type=OptionModel.BOOLEAN, value=val)
            self.assertIs(opt.clean_value(), False, msg=f"value={val!r}")

    def test_clean_value_boolean_invalid_raises(self):
        opt = OptionModel(key="test_bool_bad", type=OptionModel.BOOLEAN, value="maybe")
        with self.assertRaises(ValueError) as ctx:
            opt.clean_value()
        self.assertIn("Invalid boolean", str(ctx.exception))


class GetOptionTests(TestCase):
    """Tests for get_option()."""

    def setUp(self):
        cache.clear()

    def test_get_option_missing_returns_default(self):
        self.assertEqual(get_option("nonexistent_key", default="fallback"), "fallback")

    def test_get_option_missing_no_default_returns_none(self):
        self.assertIsNone(get_option("nonexistent_key"))

    def test_get_option_integer(self):
        OptionModel.objects.create(key="opt_int", type=OptionModel.INTEGER, value="10")
        self.assertEqual(get_option("opt_int"), 10)

    def test_get_option_string(self):
        OptionModel.objects.create(key="opt_str", type=OptionModel.STRING, value="hello")
        self.assertEqual(get_option("opt_str"), "hello")

    def test_get_option_float(self):
        OptionModel.objects.create(key="opt_float", type=OptionModel.FLOAT, value="2.5")
        self.assertEqual(get_option("opt_float"), 2.5)

    def test_get_option_boolean(self):
        OptionModel.objects.create(key="opt_bool", type=OptionModel.BOOLEAN, value="True")
        self.assertIs(get_option("opt_bool"), True)


class SetOptionTests(TestCase):
    """Tests for set_option()."""

    def setUp(self):
        cache.clear()

    def test_set_option_creates_and_get_returns(self):
        set_option("new_key", "new_value")
        self.assertEqual(get_option("new_key"), "new_value")

    def test_set_option_infers_type_bool(self):
        set_option("bool_key", True)
        obj = OptionModel.objects.get(key="bool_key")
        self.assertEqual(obj.type, OptionModel.BOOLEAN)
        self.assertEqual(obj.value, "True")

    def test_set_option_infers_type_int(self):
        set_option("int_key", 99)
        self.assertEqual(get_option("int_key"), 99)


class ImportDataCommandTests(TestCase):
    """Tests for import_data management command."""

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
        self.assertEqual(site_name_opt.value, "My Site")
