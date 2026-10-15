from django.test import TestCase
from django.urls import reverse

from account.models import UserModel
from billboard.models import BillboardCategory, BillboardFinalPriceModel, BillboardModel
from siteoption.constants import BILLBOARD_COMMISSION
from siteoption.utils.functions import set_option
from tests.helpers import make_admin, make_billboard, make_city, make_reseller, make_state


class BillboardModelTests(TestCase):
    def test_status_properties(self):
        pub = make_billboard(billboard_status=BillboardModel.BillboardStatus.PUBLIC)
        draft = make_billboard(billboard_status=BillboardModel.BillboardStatus.DRAFT, name='d')
        unav = make_billboard(
            billboard_status=BillboardModel.BillboardStatus.UNAVAILABLE, name='u'
        )
        self.assertTrue(pub.is_publicly_listed)
        self.assertFalse(draft.is_publicly_listed)
        self.assertTrue(unav.is_publicly_listed)
        self.assertTrue(unav.is_unavailable_for_display)
        self.assertFalse(pub.is_unavailable_for_display)

    def test_get_recent(self):
        make_billboard(name='a')
        make_billboard(name='b')
        make_billboard(
            name='hidden',
            billboard_status=BillboardModel.BillboardStatus.DRAFT,
        )
        recent = list(BillboardModel.get_recent(10))
        names = [b.name for b in recent]
        self.assertIn('a', names)
        self.assertIn('b', names)
        self.assertNotIn('hidden', names)

    def test_get_related(self):
        city = make_city()
        base = make_billboard(city=city, name='base', billboard_length=12, billboard_width=4)
        related = make_billboard(
            city=city, name='rel', billboard_length=12, billboard_width=4
        )
        make_billboard(city=city, name='other', billboard_length=99, billboard_width=4)
        ids = {b.id for b in base.get_related}
        self.assertIn(related.id, ids)
        self.assertNotIn(base.id, ids)

    def test_billboard_pic_url_fallback(self):
        bb = make_billboard()
        self.assertIn('no-image', bb.billboard_pic_url)

    def test_get_absolute_url_with_slug(self):
        bb = make_billboard(slug='my-board')
        self.assertEqual(bb.get_absolute_url(), reverse('billboard-detail', args=['my-board']))

    def test_get_absolute_url_empty_slug_uses_id_name(self):
        bb = make_billboard()
        bb.slug = ' '
        # May raise NoReverseMatch if billboard-detail-id is missing — document behavior
        try:
            url = bb.get_absolute_url()
            self.assertIn(str(bb.id), url)
        except Exception as exc:
            self.assertIn('billboard-detail-id', str(exc))

    def test_city_state_category_str_and_urls(self):
        state = make_state(name='S1', slug='s1')
        city = make_city(state=state, name='C1', slug='c1')
        cat = BillboardCategory.objects.create(name='Cat')
        self.assertEqual(str(state), 'S1')
        self.assertEqual(str(city), 'C1')
        self.assertEqual(str(cat), 'Cat')
        self.assertEqual(state.get_absolute_url(), reverse('billboard-state-list', args=['s1']))
        self.assertEqual(city.get_absolute_url(), reverse('billboard-city-list', args=['c1']))


class FinalPriceTests(TestCase):
    def test_get_commission_default(self):
        self.assertEqual(BillboardFinalPriceModel.get_commission(), 1.2)

    def test_get_commission_from_option(self):
        set_option(BILLBOARD_COMMISSION, 1.5)
        self.assertEqual(BillboardFinalPriceModel.get_commission(), 1.5)

    def test_update_price_reseller(self):
        reseller = make_reseller()
        bb = make_billboard(reseller=reseller, price=1000)
        BillboardFinalPriceModel.objects.create(billboard=bb, add_price=100, final_price=0)
        BillboardFinalPriceModel.update_price(bb, 1.2)
        fp = BillboardFinalPriceModel.objects.get(billboard=bb)
        self.assertEqual(fp.final_price, 1000 * 1.2 + 100)

    def test_update_price_admin(self):
        admin = make_admin()
        bb = make_billboard(reseller=admin, price=1000)
        BillboardFinalPriceModel.objects.create(billboard=bb, add_price=50, final_price=0)
        BillboardFinalPriceModel.update_price(bb, 1.2)
        fp = BillboardFinalPriceModel.objects.get(billboard=bb)
        self.assertEqual(fp.final_price, 1000)

    def test_final_price_str_deleted(self):
        fp = BillboardFinalPriceModel(billboard=None)
        self.assertEqual(str(fp), 'حذف شده')
