from django.test import TestCase
from django.urls import reverse

from tests.helpers import make_admin, make_billboard, make_reseller
from tests.helpers.media import put_storage_file


class MediaLibraryJsonTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        path = put_storage_file('billboard/2026/10/15/m.jpg', b'data')
        bb = make_billboard(reseller=self.admin, name='M')
        bb.billboard_pic = path
        bb.save(update_fields=['billboard_pic'])
        self.url = reverse('admin:billboard_billboardmodel_media_library')

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (302, 403))

    def test_json_ok(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url, {'page': 'bad', 'page_size': 'x', 'q': 'm.jpg'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(data['page'], 1)
