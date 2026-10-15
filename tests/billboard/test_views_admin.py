from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from billboard.models import BillboardCategory, BillboardModel
from billboard.views import _parse_billboard_id_list
from tests.helpers import make_admin, make_billboard, make_company, make_reseller


class ParseIdListTests(TestCase):
    def test_parse(self):
        self.assertEqual(_parse_billboard_id_list('1, 2,,x,3'), [1, 2, 3])
        self.assertEqual(_parse_billboard_id_list(''), [])
        self.assertEqual(_parse_billboard_id_list(None), [])


class AssignViewsTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)
        self.bb1 = make_billboard(name='A')
        self.bb2 = make_billboard(name='B')
        self.company = make_company()
        self.category = BillboardCategory.objects.create(name='Cat1')

    def test_assign_company_get(self):
        url = reverse('admin:billboard_billboardmodel_assign_to_company')
        response = self.client.get(url, {'ids': f'{self.bb1.id},{self.bb2.id}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['company_count'], 2)

    def test_assign_company_post(self):
        url = reverse('admin:billboard_billboardmodel_assign_to_company')
        response = self.client.post(url, {
            'ids': f'{self.bb1.id},{self.bb2.id}',
            'company_id': str(self.company.id),
        })
        self.assertEqual(response.status_code, 302)
        self.bb1.refresh_from_db()
        self.assertEqual(self.bb1.owner_company_id, self.company.id)

    def test_assign_company_clear(self):
        self.bb1.owner_company = self.company
        self.bb1.save(update_fields=['owner_company'])
        url = reverse('admin:billboard_billboardmodel_assign_to_company')
        self.client.post(url, {'ids': str(self.bb1.id), 'company_id': ''})
        self.bb1.refresh_from_db()
        self.assertIsNone(self.bb1.owner_company_id)

    def test_assign_company_empty_ids(self):
        url = reverse('admin:billboard_billboardmodel_assign_to_company')
        response = self.client.post(url, {'ids': '', 'company_id': str(self.company.id)})
        self.assertEqual(response.status_code, 302)

    def test_assign_category_post(self):
        url = reverse('admin:billboard_billboardmodel_assign_to_category')
        response = self.client.post(url, {
            'ids': str(self.bb1.id),
            'category_id': str(self.category.id),
        })
        self.assertEqual(response.status_code, 302)
        self.bb1.refresh_from_db()
        self.assertEqual(self.bb1.category_id, self.category.id)

    def test_assign_category_invalid(self):
        url = reverse('admin:billboard_billboardmodel_assign_to_category')
        response = self.client.post(url, {
            'ids': str(self.bb1.id),
            'category_id': 'abc',
        })
        self.assertEqual(response.status_code, 302)


class ImportPermissionTests(TestCase):
    def test_import_requires_permission(self):
        user = make_reseller()
        self.client.force_login(user)
        url = reverse('admin:billboard_billboardmodel_import')
        response = self.client.get(url)
        self.assertIn(response.status_code, (302, 403))

    def test_import_allowed_with_permission(self):
        user = make_admin()
        ct = ContentType.objects.get_for_model(BillboardModel)
        perm = Permission.objects.get(content_type=ct, codename='can_import_billboard')
        user.user_permissions.add(perm)
        self.client.force_login(user)
        url = reverse('admin:billboard_billboardmodel_import')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
