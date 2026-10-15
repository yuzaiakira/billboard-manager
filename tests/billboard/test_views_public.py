from django.test import TestCase
from django.urls import reverse

from billboard.models import BillboardModel
from tests.helpers import make_billboard, make_city, make_state


class PublicViewTests(TestCase):
    def setUp(self):
        self.state = make_state(name='Tehran', slug='tehran')
        self.city = make_city(state=self.state, name='TehranCity', slug='tehran-city')
        self.public = make_billboard(city=self.city, name='Public BB', slug='public-bb')
        self.draft = make_billboard(
            city=self.city,
            name='Draft BB',
            slug='draft-bb',
            billboard_status=BillboardModel.BillboardStatus.DRAFT,
        )
        self.unavailable = make_billboard(
            city=self.city,
            name='Unav BB',
            slug='unav-bb',
            billboard_status=BillboardModel.BillboardStatus.UNAVAILABLE,
        )

    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('queryset', response.context)

    def test_list(self):
        response = self.client.get(reverse('billboard-list'))
        self.assertEqual(response.status_code, 200)
        names = [o.name for o in response.context['object_list']]
        self.assertIn('Public BB', names)
        self.assertNotIn('Draft BB', names)

    def test_detail_public(self):
        response = self.client.get(reverse('billboard-detail', args=['public-bb']))
        self.assertEqual(response.status_code, 200)

    def test_detail_draft_404(self):
        response = self.client.get(reverse('billboard-detail', args=['draft-bb']))
        self.assertEqual(response.status_code, 404)

    def test_detail_unavailable_ok(self):
        response = self.client.get(reverse('billboard-detail', args=['unav-bb']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_unavailable_for_display'])

    def test_city_list(self):
        response = self.client.get(reverse('billboard-city-list', args=['tehran-city']))
        self.assertEqual(response.status_code, 200)

    def test_state_list(self):
        response = self.client.get(reverse('billboard-state-list', args=['tehran']))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get(reverse('search'), {'q': 'Public', 'cities': 'all'})
        self.assertEqual(response.status_code, 200)
        names = [o.name for o in response.context['object_list']]
        self.assertIn('Public BB', names)

    def test_search_filters_city(self):
        other_city = make_city(state=self.state, name='Other', slug='other')
        make_billboard(city=other_city, name='OtherBB', slug='other-bb')
        response = self.client.get(
            reverse('search'),
            {'q': 'BB', 'cities': str(self.city.id)},
        )
        names = [o.name for o in response.context['object_list']]
        self.assertIn('Public BB', names)
        self.assertNotIn('OtherBB', names)
