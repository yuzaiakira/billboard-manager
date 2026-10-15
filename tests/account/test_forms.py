from django.test import TestCase

from account.forms import UserRegisterForm
from tests.helpers import make_user


class UserRegisterFormTests(TestCase):
    def test_valid_form(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'a@b.com',
            'first_name': 'Ali',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        form = UserRegisterForm(data={
            'username': 'newuser2',
            'email': 'a@b.com',
            'first_name': 'Ali',
            'password1': 'ComplexPass123!',
            'password2': 'OtherPass123!',
        })
        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        make_user(username='taken')
        form = UserRegisterForm(data={
            'username': 'taken',
            'email': 'a@b.com',
            'first_name': 'Ali',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertFalse(form.is_valid())
