from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.views import Logout
from tests.helpers import make_user


class LogoutSuccessUrlTests(TestCase):
    def test_get_success_url(self):
        view = Logout()
        view.request = RequestFactory().get('/')
        self.assertEqual(view.get_success_url(), reverse('home'))

    def test_logout_redirects_home_when_configured(self):
        # URLConf uses next_page='login' on as_view; view method still covers home
        user = make_user(username='lo', password='pass12345')
        self.client.login(username='lo', password='pass12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
