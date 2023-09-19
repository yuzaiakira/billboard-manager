from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key

class Command(BaseCommand):
    help = "get secret key for replace settings.SECRET_KEY "

    def handle(self, *args, **options):
        print("django-insecure-" + get_random_secret_key())