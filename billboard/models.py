from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.templatetags.static import static
# source: https://pypi.org/project/django-jalali/
from django_jalali.db import models as jmodels

from account.models import UserModel
from seo.models import SEOBaseModel
from billboard.utils import billboard_path
from billboard.manager import BillboardManager
from billboard.mixin import ImageCompressMixin
from siteoption.utils.functions import get_option

# Create your models here.


class StateModel(SEOBaseModel):
    name = models.CharField(max_length=100, verbose_name="نام استان")

    class Meta:
        verbose_name_plural = "استان ها"
        verbose_name = "استان"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('billboard-state-list', args=[self.slug])


class CityModel(SEOBaseModel):
    state = models.ForeignKey('StateModel', related_name='CityModel', on_delete=models.CASCADE, verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    class Meta:
        verbose_name_plural = "شهر ها"
        verbose_name = "شهر"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('billboard-city-list', args=[self.slug])


class BillboardCategory(SEOBaseModel):
    parent = models.ForeignKey('self', related_name='BillboardCategory',
                               on_delete=models.CASCADE, verbose_name="دسته بندی", blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name="اسم دسته بندی")
    billboard_visibility = models.BooleanField(verbose_name="نمایش بیلبورد ها در این دسته بندی؟", default=True)
    priority = models.SmallIntegerField(verbose_name="اولیت", blank=True, default=0)

    class Meta:
        verbose_name_plural = "دسته بندی ها"
        verbose_name = "دسته بندی"

    def __str__(self):
        return self.name


class BillboardAttributeModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام ویژگی بیلبورد")

    class Meta:
        verbose_name_plural = "ویژگی های بیلبورد"
        verbose_name = "ویژگی بیلبورد"

    def __str__(self):
        return self.name


class BillboardModel(SEOBaseModel):
    city = models.ForeignKey('CityModel', related_name='BillboardModel', on_delete=models.SET_NULL,
                             verbose_name="شهر", null=True)
    category = models.ForeignKey(BillboardCategory, related_name='BillboardModel', on_delete=models.SET_NULL,
                                 verbose_name="دسته بندی", blank=True, null=True)

    name = models.CharField(max_length=100, verbose_name="نام بیلبورد")
    address = models.CharField(max_length=250, verbose_name="محل بیلبورد")
    attribute = models.ManyToManyField(BillboardAttributeModel,
                                       verbose_name="ویژگی های بیلبورد", blank=True, null=True)
    description = models.TextField(verbose_name='توضیحات بیلبورد', blank=True)

    has_power = models.BooleanField(verbose_name="روشنایی", default=True)
    billboard_length = models.DecimalField(max_digits=7, decimal_places=3, verbose_name="طول بیلبورد")
    billboard_width = models.DecimalField(max_digits=7, decimal_places=3, verbose_name="عرض بیلبورد")

    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    reservation_date = jmodels.jDateField(verbose_name="تاریخ اکران", null=True)
    reseller = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name="نماینده", blank=True, null=True)

    map_iframe = models.TextField(verbose_name='نقشه', blank=True, null=True)
    billboard_pic = models.ImageField(upload_to=billboard_path, verbose_name="تصویر اصلی بیلبورد",
                                      blank=True, null=True)

    BILLBOARD_PUBLIC = 0
    BILLBOARD_DRAFT = 1
    BILLBOARD_ARCHIVE = 2
    BILLBOARD_NO_SELL = 3

    billboard_group_status = (
        (BILLBOARD_PUBLIC, 'نمایش در سایت'),
        (BILLBOARD_DRAFT, 'پیش نویس'),
        (BILLBOARD_ARCHIVE, 'آرشیو'),
        (BILLBOARD_NO_SELL, 'غیر قابل فروش'),
    )

    billboard_status = models.PositiveSmallIntegerField(choices=billboard_group_status,
                                                        verbose_name="وضعیت بیلبورد", default=0)

    # manager
    objects = BillboardManager()

    # The fields that show in short property
    fields_property = ['name', 'address', 'has_power', 'reservation_date']

    class Meta:
        verbose_name_plural = "بیلبورد ها"
        verbose_name = "بیلبورد"
        permissions = (("can_import_billboard", "اجاره وارد کردن گروهی بیلبورد"),)

    def __str__(self):
        return self.name

    @classmethod
    def get_recent(cls, number, only=None):
        """Return of newest object the number of "number"

        ...

        Parameters
        ----------
        number : int
            the number of object to returned

        only : list
            list of the field in the model that you want to be return
            like: only=['name', 'price', ... ]
            default is self.fields_property

        Returns
        -------
        return a  QuerySet[BillboardModel] by number of 'number'

        """
        if only is None:
            only = cls.fields_property

        return cls.objects.order_by('-id').only(*only)[:number]

    @property
    def get_related(self):
        """Return related object with count of 3"""

        return BillboardModel.objects.filter(~Q(id=self.id), city=self.city, billboard_length=self.billboard_length,
                                             billboard_width=self.billboard_width,
                                             has_power=self.has_power)[:3].only(*self.fields_property)

    @property
    def billboard_pic_url(self):
        """Get picture form model if picture is null change by default picture
        you can use it in template
        """
        if self.billboard_pic and hasattr(self.billboard_pic, 'url'):
            return self.billboard_pic.url
        else:
            return static('template/images/no-image.png')

    def get_absolute_url(self):
        url = self.slug
        if url is None or url == "" or url == " ":
            return reverse('billboard-detail-id', args=[self.id])

        return reverse('billboard-detail', args=[url])

    @property
    def get_add_to_list_class(self):
        lists = self.ListModel.all()
        return lists


class BillboardFinalPriceModel(models.Model):
    billboard = models.OneToOneField(BillboardModel, on_delete=models.CASCADE,
                                     related_name="BillboardFinalPriceModel", null=True)
    add_price = models.PositiveBigIntegerField(verbose_name="قیمت افزوده",  default=0, blank=True)
    final_price = models.PositiveBigIntegerField(verbose_name="قیمت نهایی",  default=0, blank=True)


    class Meta:
        verbose_name_plural = "قیمت های نهایی"
        verbose_name = "قیمت نهایی"

    def __str__(self):
        try:
            name = self.billboard.name

        except AttributeError:
            name = "حذف شده"

        return name

    @classmethod
    def get_commission(cls):
        return get_option('BillboardCommission', 1.2)

    @classmethod
    def update_price(cls, billboard, commission):
        final_price_model, created = cls.objects.get_or_create(billboard=billboard)

        if billboard.reseller.user_group != UserModel.ADMIN_USER:
            final_price_model.final_price = (billboard.price * commission)\
                                            + billboard.BillboardFinalPriceModel.add_price
        else:
            final_price_model.final_price = billboard.price

        final_price_model.add_price = billboard.BillboardFinalPriceModel.add_price
        final_price_model.save()


class BillboardImageModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان عکس", blank=True)
    image = models.ImageField(upload_to=billboard_path, verbose_name="عکس")  # TODO: delete file when delete model
    billboard = models.ForeignKey(BillboardModel, related_name="BillboardImageModel",
                                  verbose_name="تصویر بیلبورد",  on_delete=models.CASCADE, null=True)
    uploader = models.ForeignKey(UserModel, related_name="BillboardImageModel",
                                 verbose_name="آپلود کننده", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = "عکس های بیلبورد"
        verbose_name = "عکس بیلبورد"

    def __str__(self):
        return self.title
