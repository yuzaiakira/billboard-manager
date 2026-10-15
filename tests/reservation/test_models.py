import jdatetime
from django.test import TestCase

from reservation.models import ContractModel, RentalListModel
from tests.helpers import make_billboard, make_brand


class ReservationModelTests(TestCase):
    def setUp(self):
        self.brand = make_brand(brand_name='Brand A')
        self.billboard = make_billboard(name='BB1')
        self.contract = ContractModel.objects.create(
            brand=self.brand,
            date=jdatetime.date(1403, 1, 1),
            name='C1',
        )

    def test_contract_str_name(self):
        self.assertEqual(str(self.contract), 'C1')

    def test_contract_str_date_fallback(self):
        c = ContractModel.objects.create(
            brand=self.brand,
            date=jdatetime.date(1403, 2, 1),
            name=None,
        )
        self.assertEqual(str(c), str(c.date))

    def test_rental_str(self):
        rental = RentalListModel.objects.create(
            contract=self.contract,
            billboard=self.billboard,
            start_date=jdatetime.date(1403, 1, 1),
            end_date=jdatetime.date(1403, 2, 1),
        )
        self.assertIn('BB1', str(rental))
        self.assertIn('Brand A', str(rental))

    def test_get_rental_list(self):
        RentalListModel.objects.create(
            contract=self.contract,
            billboard=self.billboard,
            start_date=jdatetime.date(1403, 1, 1),
            end_date=jdatetime.date(1403, 2, 1),
        )
        other = make_billboard(name='BB2')
        qs = RentalListModel.get_rental_list(self.billboard.id)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(RentalListModel.get_rental_list(other.id).count(), 0)
