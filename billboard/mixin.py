import os
from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
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

    def _is_new_upload(self, field_name: str) -> bool:
        """Return True only for real HTTP uploads (not library path reuse)."""
        if getattr(self, '_skip_image_compress', False):
            return False
        field_file = getattr(self, field_name, None)
        if not field_file:
            return False
        file_obj = getattr(field_file, 'file', field_file)
        return isinstance(file_obj, UploadedFile)

    def _should_compress_image(self, field_name: str) -> bool:
        return self._image_field_changed(field_name) and self._is_new_upload(field_name)

    def assign_existing_image(self, field_name: str, storage_path: str) -> None:
        """Point an ImageField at an existing storage path without re-uploading."""
        # Set attname directly so Django does not treat this as a new upload.
        field = self._meta.get_field(field_name)
        setattr(self, field.attname, storage_path)
        self._skip_image_compress = True

    @staticmethod
    def compress(image):
        im = Image.open(image)
        im = im.convert('RGB')
        im_io = BytesIO()
        im.save(im_io, 'JPEG', quality=60)
        # basename prevents upload_to from nesting date paths on re-save
        filename = os.path.basename(image.name)
        return File(im_io, name=filename)
