class ImageCompressMixin:

    def save(self, *args, **kwargs):
        print('hiiiiiiiiiiiii')
        super().save(*args, **kwargs)