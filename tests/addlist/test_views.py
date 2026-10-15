from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from addlist.models import ListsModel
from addlist.templatetags.check_in_list import on_list
from addlist.views import WatchList, normalize_decimal
from tests.helpers import make_admin, make_billboard, make_user


class NormalizeDecimalTests(TestCase):
    def test_values(self):
        self.assertEqual(normalize_decimal(5.000), '5')
        self.assertEqual(normalize_decimal(5.500), '5.5')
        self.assertEqual(normalize_decimal(None), '')
        self.assertEqual(normalize_decimal('x'), 'x')


class AddListViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='lister', password='pass12345')
        self.bb = make_billboard(name='Listed')
        self.client.login(username='lister', password='pass12345')

    def test_add_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('add-to-list', args=[self.bb.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_and_remove(self):
        response = self.client.get(reverse('add-to-list', args=[self.bb.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['added'])
        self.assertTrue(ListsModel.objects.filter(user=self.user, billboard=self.bb).exists())

        response = self.client.get(reverse('add-to-list', args=[self.bb.id]))
        self.assertFalse(response.json()['added'])
        self.assertTrue(response.json()['in_list'])

        response = self.client.get(reverse('remove-from-list', args=[self.bb.id]))
        self.assertTrue(response.json()['deleted'])
        self.assertFalse(ListsModel.objects.filter(user=self.user, billboard=self.bb).exists())

    def test_watchlist_and_clear(self):
        ListsModel.objects.create(user=self.user, billboard=self.bb)
        response = self.client.get(reverse('WatchList'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)

        response = self.client.get(reverse('remove-list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ListsModel.objects.filter(user=self.user).count(), 0)

    def test_export_excel(self):
        ListsModel.objects.create(user=self.user, billboard=self.bb)
        response = self.client.get(reverse('get-excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/ms-excel')

    def test_pdf_view(self):
        ListsModel.objects.create(user=self.user, billboard=self.bb)
        response = self.client.get(reverse('get-pdf'), {'billboard_pic': 'on', 'city': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_watchlist_context_not_shared_across_users(self):
        other = make_user(username='other_lister', password='pass12345')
        ListsModel.objects.create(user=self.user, billboard=self.bb)
        other_bb = make_billboard(name='OtherListed')
        ListsModel.objects.create(user=other, billboard=other_bb)

        factory = RequestFactory()
        view = WatchList()
        req1 = factory.get('/account/list/')
        req1.user = self.user
        resp1 = view.get(req1)
        self.assertEqual(len(resp1.context_data['object_list'] if hasattr(resp1, 'context_data') else view.context['object_list']), 1)

        req2 = factory.get('/account/list/')
        req2.user = other
        view2 = WatchList()
        resp2 = view2.get(req2)
        # Class-level context may leak; assert second request sees other's list size
        self.assertEqual(len(view2.context['object_list']), 1)
        self.assertEqual(view2.context['object_list'][0].user_id, other.id)


class OnListFilterTests(TestCase):
    def test_anonymous_false(self):
        bb = make_billboard()
        self.assertFalse(on_list(bb, AnonymousUser()))

    def test_in_and_out(self):
        user = make_user(username='f1')
        bb = make_billboard()
        self.assertFalse(on_list(bb, user))
        ListsModel.objects.create(user=user, billboard=bb)
        self.assertTrue(on_list(bb, user))


class AdminWatchlistViewsTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.user = make_user(username='watched')
        self.bb = make_billboard()
        ListsModel.objects.create(user=self.user, billboard=self.bb)

    def test_denied_for_normal(self):
        self.client.force_login(self.user)
        from addlist.admin_views import watchlist_users_list_view
        from django.core.exceptions import PermissionDenied
        from django.test import RequestFactory

        request = RequestFactory().get('/')
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            watchlist_users_list_view(request)

    def test_admin_list_and_detail(self):
        from addlist.admin_views import watchlist_user_detail_view, watchlist_users_list_view
        from django.test import RequestFactory

        request = RequestFactory().get('/')
        request.user = self.admin
        response = watchlist_users_list_view(request)
        self.assertEqual(response.status_code, 200)
        response = watchlist_user_detail_view(request, self.user.id)
        self.assertEqual(response.status_code, 200)
