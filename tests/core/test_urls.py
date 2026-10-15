from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


class CoreUrlTests(SimpleTestCase):
    def test_named_urls_resolve(self):
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(reverse('login'), '/account/login/')
        self.assertEqual(reverse('billboard-list'), '/billboards')
        self.assertEqual(reverse('add-to-list', args=[1]), '/add-to-list/1')
        self.assertEqual(reverse('WatchList'), '/account/list/')

    def test_auth_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'account.UserModel')
