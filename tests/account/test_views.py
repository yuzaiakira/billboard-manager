from django.test import TestCase
from django.urls import reverse

from siteoption.constants import SITE_NAME
from siteoption.utils.functions import set_option
from tests.helpers import make_user


class AccountViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='loginuser', password='pass12345')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'pass12345',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any('Invalid username or password' in m for m in messages))

    def test_login_site_name_from_option(self):
        set_option(SITE_NAME, 'My Billboard')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.context['site_name'], 'My Billboard')

    def test_login_redirects_authenticated(self):
        self.client.login(username='loginuser', password='pass12345')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)

    def test_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'newbie',
            'email': 'n@e.com',
            'first_name': 'New',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_logout(self):
        self.client.login(username='loginuser', password='pass12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
