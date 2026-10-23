"""Themed 4xx/5xx error pages."""

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import bad_request, page_not_found, permission_denied, server_error


@override_settings(DEBUG=False)
class Http404ErrorPageTests(TestCase):
    def test_404_uses_themed_template(self):
        response = self.client.get('/no-such-page-xyz-anten-404/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, 'یافت نشد', status_code=404)
        self.assertContains(response, reverse('home'), status_code=404)


class ErrorTemplateRenderTests(TestCase):
    """Render default handlers against our themed templates."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_400_template(self):
        request = self.factory.get('/')
        response = bad_request(request, exception=SuspiciousOperation('bad'))
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '400', status_code=400)
        self.assertContains(response, 'نامعتبر', status_code=400)
        self.assertContains(response, 'error-code', status_code=400)

    def test_403_template(self):
        request = self.factory.get('/')
        response = permission_denied(request, exception=PermissionDenied())
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '403', status_code=403)
        self.assertContains(response, 'دسترسی', status_code=403)
        self.assertContains(response, reverse('login'), status_code=403)

    def test_404_template(self):
        request = self.factory.get('/missing/')
        response = page_not_found(request, exception=Exception('missing'))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, reverse('billboard-list'), status_code=404)

    def test_500_template(self):
        request = self.factory.get('/')
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, '500', status_code=500)
        self.assertContains(response, 'مشکلی پیش آمده', status_code=500)
        # 500 must not depend on site_name context processor
        self.assertContains(response, 'آنتن', status_code=500)
