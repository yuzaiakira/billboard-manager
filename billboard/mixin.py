from io import BytesIO
from PIL import Image
from django.core.files import File


class ImageCompressMixin:
    @staticmethod
    def compress(image):
        im = Image.open(image)
        im = im.convert('RGB')
        im_io = BytesIO()
        im.save(im_io, 'JPEG', quality=60)
        new_image = File(im_io, name=image.name)
        return new_image
