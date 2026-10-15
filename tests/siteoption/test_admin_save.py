from django.contrib.admin.sites import AdminSite
from django.core.cache import cache
from django.test import RequestFactory, TestCase

from siteoption.admin import OptionModelAdmin
from siteoption.models import OptionModel
from siteoption.utils.functions import get_option, set_option
from tests.helpers import make_admin


class OptionAdminSaveTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin_user = make_admin()
        self.model_admin = OptionModelAdmin(OptionModel, AdminSite())

    def test_save_model_invalidates_cache(self):
        set_option('adm_key', 'old')
        self.assertEqual(get_option('adm_key'), 'old')
        obj = OptionModel.objects.get(key='adm_key')
        obj.value = 'new'
        request = RequestFactory().post('/')
        request.user = self.admin_user
        form = self.model_admin.get_form(request)(instance=obj, data={
            'key': 'adm_key',
            'type': OptionModel.STRING,
            'value': 'new',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.model_admin.save_model(request, form.save(commit=False), form, change=True)
        self.assertEqual(get_option('adm_key'), 'new')
