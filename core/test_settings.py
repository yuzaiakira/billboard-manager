"""Test settings: SQLite + fast password hasher + isolated MEDIA_ROOT."""
import tempfile

from core.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MEDIA_ROOT = tempfile.mkdtemp(prefix='billboard_test_media_')
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
