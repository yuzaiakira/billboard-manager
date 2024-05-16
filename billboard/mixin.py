from io import BytesIO
from PIL import Image
from django.core.files import File
import os


class ImageCompressMixin:
    def compress(self, image):
        image_name = image.path.split('.')[:-1]
        image_name = ''.join(image_name)
        new_image_name = f'{image_name}.jpeg'
        new_image_name = os.path.basename(new_image_name)
        im = Image.open(image)
        im = im.convert('RGB')

        im.save(new_image_name)
        im = Image.open(new_image_name)

        im_io = BytesIO()
        im.save(im_io, 'JPEG', optimize=True, quality=60)

        return File(im_io, name=new_image_name)
