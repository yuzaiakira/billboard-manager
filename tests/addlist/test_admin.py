from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse

from addlist.admin import ListsModelAdmin
from addlist.models import ListsModel
from tests.helpers import make_admin, make_billboard, make_user


class ListsAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin_model = ListsModelAdmin(ListsModel, self.site)
        self.factory = RequestFactory()
        self.admin = make_admin()
        self.user = make_user(username='wl')
        self.bb = make_billboard()
        ListsModel.objects.create(user=self.user, billboard=self.bb)

    def test_str(self):
        item = ListsModel.objects.get(user=self.user)
        self.assertIn(str(self.user), str(item))

    def test_changelist_shows_link_for_admin(self):
        self.client.force_login(self.admin)
        url = reverse('admin:addlist_listsmodel_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('show_watchlist_users_link'))

    def test_custom_urls_resolve(self):
        self.client.force_login(self.admin)
        list_url = reverse('admin:addlist_listsmodel_watchlist_users')
        detail_url = reverse(
            'admin:addlist_listsmodel_watchlist_user_detail',
            args=[self.user.id],
        )
        self.assertEqual(self.client.get(list_url).status_code, 200)
        self.assertEqual(self.client.get(detail_url).status_code, 200)

    def test_admin_group_user_allowed(self):
        from account.models import UserModel
        from addlist.admin_views import _require_admin_watchlist_reports

        staff = make_user(username='adm2', user_group=UserModel.ADMIN_USER, is_staff=True)
        _require_admin_watchlist_reports(staff)
