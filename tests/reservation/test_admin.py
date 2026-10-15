from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from reservation.admin import RentalListAdmin
from reservation.models import RentalListModel
from tests.helpers import make_billboard


class RentalAdminTests(TestCase):
    def test_get_form_prefills_billboard(self):
        bb = make_billboard()
        admin_model = RentalListAdmin(RentalListModel, AdminSite())
        request = RequestFactory().get('/', {'billboard_id': str(bb.id)})
        form = admin_model.get_form(request)
        self.assertEqual(form.base_fields['billboard'].initial, str(bb.id))
