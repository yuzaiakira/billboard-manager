from unittest.mock import patch

from django.test import TestCase

from billboard.utils import billboard_bool_value, billboard_path


class BillboardUtilsTests(TestCase):
    def test_billboard_bool_value(self):
        self.assertEqual(billboard_bool_value(True), 'دارد')
        self.assertEqual(billboard_bool_value(False), 'ندارد')
        self.assertEqual(billboard_bool_value(None), 'ندارد')

    @patch('billboard.utils.default_storage')
    @patch('billboard.utils.now')
    def test_billboard_path_basename(self, mock_now, mock_storage):
        class D:
            def strftime(self, fmt):
                return 'billboard/2026/10/15'

        mock_now.return_value.date.return_value = D()
        mock_storage.exists.return_value = False
        path = billboard_path(None, 'nested/dir/photo.jpg')
        self.assertEqual(path, 'billboard/2026/10/15/photo.jpg')

    @patch('billboard.utils.default_storage')
    @patch('billboard.utils.now')
    def test_billboard_path_collision_uuid(self, mock_now, mock_storage):
        class D:
            def strftime(self, fmt):
                return 'billboard/2026/10/15'

        mock_now.return_value.date.return_value = D()
        mock_storage.exists.return_value = True
        path = billboard_path(None, 'photo.jpg')
        self.assertTrue(path.startswith('billboard/2026/10/15/'))
        self.assertTrue(path.endswith('-photo.jpg') or path.endswith('photo.jpg'))
        self.assertNotEqual(path, 'billboard/2026/10/15/photo.jpg')
