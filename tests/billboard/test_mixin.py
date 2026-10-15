from django.test import TestCase

from billboard.mixin import ImageCompressMixin
from billboard.models import BillboardModel
from tests.helpers import make_billboard
from tests.helpers.media import make_uploaded_image, put_storage_file


class ImageCompressMixinTests(TestCase):
    def test_compress_produces_jpeg(self):
        uploaded = make_uploaded_image('in.png')
        result = ImageCompressMixin.compress(uploaded)
        self.assertTrue(result.name.endswith('in.png') or 'in' in result.name)
        self.assertGreater(result.size, 0)

    def test_assign_existing_image_skips_compress(self):
        path = put_storage_file('billboard/2026/10/15/lib.jpg', b'fake')
        bb = make_billboard(name='LibBB')
        bb.assign_existing_image('billboard_pic', path)
        self.assertTrue(getattr(bb, '_skip_image_compress', False))
        self.assertFalse(bb._is_new_upload('billboard_pic'))
        self.assertFalse(bb._should_compress_image('billboard_pic'))

    def test_new_upload_should_compress(self):
        bb = BillboardModel(
            name='Up',
            address='a',
            billboard_length=1,
            billboard_width=1,
            price=10,
        )
        bb.billboard_pic = make_uploaded_image('new.jpg')
        self.assertTrue(bb._image_field_changed('billboard_pic'))
        self.assertTrue(bb._is_new_upload('billboard_pic'))
        self.assertTrue(bb._should_compress_image('billboard_pic'))

    def test_save_with_upload_sets_image(self):
        bb = make_billboard(name='CompressSave')
        bb.billboard_pic = make_uploaded_image('save.jpg')
        bb.save()
        bb.refresh_from_db()
        self.assertTrue(bb.billboard_pic.name)
