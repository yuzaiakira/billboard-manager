import os
from io import BytesIO

from django.core.files import File
from PIL import Image


class ImageCompressMixin:

    def _image_field_changed(self, field_name: str) -> bool:
        """Return True only when the image was newly assigned (not on every save)."""
        field_file = getattr(self, field_name, None)
        if not field_file:
            return False
        if not self.pk:
            return True
        db_name = (
            type(self).objects.filter(pk=self.pk)
            .values_list(field_name, flat=True)
            .first()
        )
        return db_name != field_file.name

    @staticmethod
    def compress(image):
        im = Image.open(image)
        im = im.convert('RGB')
        im_io = BytesIO()
        im.save(im_io, 'JPEG', quality=60)
        # basename prevents upload_to from nesting date paths on re-save
        filename = os.path.basename(image.name)
        return File(im_io, name=filename)
