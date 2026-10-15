from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from account.models import UserModel
from billboard.admin.billboards import BillboardAdmin, export_billboards_to_xlsx_response
from billboard.admin.fieldsets import ADMIN_USER_BILLBOARD_FIELDSETS, DEFAULT_BILLBOARD_FIELDSETS
from billboard.admin.filters import BillboardResellerListFilter
from billboard.admin.inlines import BillboardFinalPriceInline, BillboardImageInline
from billboard.models import BillboardFinalPriceModel, BillboardModel
from tests.helpers import make_admin, make_billboard, make_reseller


class BillboardAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin_model = BillboardAdmin(BillboardModel, self.site)
        self.factory = RequestFactory()
        self.admin_user = make_admin()
        self.reseller = make_reseller()
        self.bb = make_billboard(reseller=self.reseller, name='AdminBB', price=200)
        BillboardFinalPriceModel.objects.create(billboard=self.bb, add_price=0, final_price=200)

    def test_fieldsets_for_roles(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertEqual(self.admin_model.get_fieldsets(request), ADMIN_USER_BILLBOARD_FIELDSETS)
        request.user = self.reseller
        self.assertEqual(self.admin_model.get_fieldsets(request), DEFAULT_BILLBOARD_FIELDSETS)

    def test_inlines_for_admin_reseller_billboard(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        admin_bb = make_billboard(reseller=self.admin_user, name='AdminOwned')
        inlines = self.admin_model.get_inlines(request, admin_bb)
        self.assertEqual(inlines, (BillboardImageInline,))

    def test_inlines_for_reseller_owned(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        inlines = self.admin_model.get_inlines(request, self.bb)
        self.assertEqual(inlines, (BillboardFinalPriceInline, BillboardImageInline))

    def test_queryset_scoped(self):
        make_billboard(reseller=make_reseller(username='r3'), name='Other')
        request = self.factory.get('/')
        request.user = self.reseller
        qs = self.admin_model.get_queryset(request)
        self.assertTrue(all(b.reseller_id == self.reseller.id for b in qs))

    def test_save_model_sets_reseller(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        obj = BillboardModel(
            name='NoReseller',
            address='a',
            billboard_length=1,
            billboard_width=1,
            price=10,
            city=self.bb.city,
        )
        self.admin_model.save_model(request, obj, form=None, change=False)
        self.assertEqual(obj.reseller_id, self.admin_user.id)

    def test_export(self):
        response = export_billboards_to_xlsx_response(BillboardModel.objects.all())
        self.assertEqual(response['Content-Type'], 'application/ms-excel')
        self.assertIn('billboard-list.xlsx', response['Content-Disposition'])

    def test_reseller_filter(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        f = BillboardResellerListFilter(
            request=request,
            params={},
            model=BillboardModel,
            model_admin=self.admin_model,
        )
        lookups = list(f.lookups(request, self.admin_model))
        self.assertTrue(any(str(self.reseller.pk) == pair[0] for pair in lookups))
        f.used_parameters = {'reseller': str(self.reseller.pk)}
        # Simulate selected value
        f = BillboardResellerListFilter(
            request=request,
            params={'reseller': str(self.reseller.pk)},
            model=BillboardModel,
            model_admin=self.admin_model,
        )
        qs = f.queryset(request, BillboardModel.objects.all())
        self.assertTrue(all(b.reseller_id == self.reseller.id for b in qs))

    def test_get_final_price(self):
        self.assertEqual(self.admin_model.get_final_price(self.bb), 200)
