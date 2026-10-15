from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from account.models import BrandModel, CompanyModel, UserModel
from reservation.models import RentalListModel
from tests.helpers import make_brand, make_company, make_user


class AccountModelTests(TestCase):
    def test_company_str(self):
        company = make_company(name='Acme')
        self.assertEqual(str(company), 'Acme')

    def test_brand_str_brand_name(self):
        brand = make_brand(brand_name='Nike')
        self.assertEqual(str(brand), 'Nike')

    def test_brand_str_agency_fallback(self):
        user = make_user(username='b1')
        brand = BrandModel.objects.create(user=user, brand_name=None, agency='Agency X')
        self.assertEqual(str(brand), 'Agency X')

    def test_brand_str_empty_fallback(self):
        user = make_user(username='b2')
        brand = BrandModel.objects.create(user=user, brand_name=None, agency=None)
        self.assertEqual(str(brand), 'وارد نشده')

    def test_can_check_reservation(self):
        user = make_user(username='perm_user')
        self.assertFalse(user.can_check_reservation)
        ct = ContentType.objects.get_for_model(RentalListModel)
        perm = Permission.objects.get(content_type=ct, codename='can_check_reservation')
        user.user_permissions.add(perm)
        user = UserModel.objects.get(pk=user.pk)
        self.assertTrue(user.can_check_reservation)
