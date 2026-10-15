from io import BytesIO

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def make_uploaded_image(name='photo.jpg', size=(40, 30), color=(200, 100, 50)):
    buf = BytesIO()
    Image.new('RGB', size, color).save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')


def put_storage_file(path, content=b'x'):
    if default_storage.exists(path):
        default_storage.delete(path)
    return default_storage.save(path, BytesIO(content))
