from django.test import RequestFactory, TestCase

from billboard.models import BillboardModel
from tests.helpers import make_admin, make_billboard, make_reseller


class BillboardManagerTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.reseller = make_reseller()
        self.other = make_reseller(username='other')
        self.public = make_billboard(reseller=self.reseller, name='Pub')
        self.draft = make_billboard(
            reseller=self.reseller,
            name='Draft',
            billboard_status=BillboardModel.BillboardStatus.DRAFT,
        )
        self.archive = make_billboard(
            reseller=self.reseller,
            name='Arch',
            billboard_status=BillboardModel.BillboardStatus.ARCHIVE,
        )
        self.unavailable = make_billboard(
            reseller=self.reseller,
            name='Unav',
            billboard_status=BillboardModel.BillboardStatus.UNAVAILABLE,
        )
        make_billboard(reseller=self.other, name='OtherBB')

    def test_publicly_listed_excludes_draft_archive(self):
        names = set(BillboardModel.objects.publicly_listed().values_list('name', flat=True))
        self.assertIn('Pub', names)
        self.assertIn('Unav', names)
        self.assertNotIn('Draft', names)
        self.assertNotIn('Arch', names)

    def test_by_reseller_admin_sees_all(self):
        request = RequestFactory().get('/')
        request.user = self.admin
        self.assertEqual(BillboardModel.objects.by_reseller(request).count(), 5)

    def test_by_reseller_filters(self):
        request = RequestFactory().get('/')
        request.user = self.reseller
        qs = BillboardModel.objects.by_reseller(request)
        self.assertEqual(qs.count(), 4)
        self.assertTrue(all(b.reseller_id == self.reseller.id for b in qs))
