from unittest.mock import patch

from django.test import TestCase

from billboard.media_library import list_media_for_user, resolve_library_path
from billboard.models import BillboardImageModel
from tests.helpers import make_admin, make_billboard, make_reseller
from tests.helpers.media import put_storage_file


class MediaLibraryTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.reseller = make_reseller()
        self.path_a = put_storage_file('billboard/2026/10/01/a.jpg', b'a')
        self.path_b = put_storage_file('billboard/2026/10/02/b.jpg', b'b')
        self.bb = make_billboard(reseller=self.reseller, name='R1')
        self.bb.billboard_pic = self.path_a
        self.bb.save(update_fields=['billboard_pic'])
        other = make_billboard(reseller=make_reseller(username='r2'), name='R2')
        other.billboard_pic = self.path_b
        other.save(update_fields=['billboard_pic'])
        BillboardImageModel.objects.create(
            title='img',
            image=self.path_a,
            billboard=self.bb,
            uploader=self.reseller,
        )

    def test_resolve_library_path_ok(self):
        self.assertEqual(resolve_library_path(self.path_a), self.path_a)

    def test_resolve_library_path_rejects_traversal(self):
        self.assertIsNone(resolve_library_path('../etc/passwd'))
        self.assertIsNone(resolve_library_path('billboard/../secret.jpg'))

    def test_resolve_library_path_empty_missing(self):
        self.assertIsNone(resolve_library_path(''))
        self.assertIsNone(resolve_library_path(None))
        self.assertIsNone(resolve_library_path('missing/nope.jpg'))

    def test_list_admin_sees_all_existing(self):
        data = list_media_for_user(self.admin)
        paths = {r['path'] for r in data['results']}
        self.assertIn(self.path_a, paths)
        self.assertIn(self.path_b, paths)

    def test_list_reseller_scoped(self):
        data = list_media_for_user(self.reseller)
        paths = {r['path'] for r in data['results']}
        self.assertIn(self.path_a, paths)
        self.assertNotIn(self.path_b, paths)

    def test_list_query_and_pagination(self):
        data = list_media_for_user(self.admin, query='a.jpg', page=1, page_size=1)
        self.assertEqual(data['page_size'], 1)
        self.assertTrue(all('a.jpg' in r['name'] for r in data['results']))

    def test_list_skips_missing_storage(self):
        with patch('billboard.media_library.default_storage') as storage:
            storage.exists.side_effect = lambda p: p == self.path_a
            storage.url.return_value = '/media/x'
            data = list_media_for_user(self.admin)
        paths = {r['path'] for r in data['results']}
        self.assertIn(self.path_a, paths)
        self.assertNotIn(self.path_b, paths)

    def test_page_clamping(self):
        data = list_media_for_user(self.admin, page=0, page_size=999)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 100)
