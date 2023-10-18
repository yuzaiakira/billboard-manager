from django.db import models
from account.models import BrandModel
from billboard.models import BillboardModel

from django_jalali.db import models as jmodels
# Create your models here.


class ContractModel(models.Model):
    brand = models.ForeignKey(BrandModel, verbose_name="برند", related_name='ContractModel', on_delete=models.CASCADE)
    date = jmodels.jDateField(verbose_name="تاریخ قراداد")
    name = models.CharField(max_length=255, verbose_name="نام", blank=True, null=True)

    class Meta:
        verbose_name_plural = "قرارداد ها"
        verbose_name = "قرارداد"

    def __str__(self):
        if self.name is not None:
            return self.name
        elif self.date is not None:
            return str(self.date)

        return ""


class RentalListModel(models.Model):
    contract = models.ForeignKey(ContractModel, verbose_name="قرداد",
                                 related_name='RentalListModel', on_delete=models.CASCADE)
    billboard = models.ForeignKey(BillboardModel, verbose_name="بیلبورد",
                                  related_name='RentalListModel', on_delete=models.CASCADE)

    start_date = jmodels.jDateField(verbose_name="تاریخ شروع قراداد")
    end_date = jmodels.jDateField(verbose_name="تاریخ پایان قراداد")
    months = models.PositiveSmallIntegerField(verbose_name="تعداد ماه های قراداد", blank=True, null=True)
    price = models.PositiveBigIntegerField(verbose_name="قیمت هر ماه", blank=True, null=True)

    class Meta:
        verbose_name_plural = "رزرو ها"
        verbose_name = "رزرو"
        permissions = (("can_check_reservation", "اجاره برسی رزرو ها"),)

    def __str__(self):
        return f"{self.billboard.name} - {self.contract.brand.brand_name}"

    @classmethod
    def get_rental_list(cls, billboard_id):
        return RentalListModel.objects.filter(billboard_id=billboard_id)
