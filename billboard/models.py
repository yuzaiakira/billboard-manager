from django.db import models
from django.templatetags.static import static
# source: https://pypi.org/project/django-jalali/
from django_jalali.db import models as jmodels

from adminpanel.models import UserModel
from .utils import billboard_path

# Create your models here.


class StateModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام استان")

    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        verbose_name_plural = "استان ها"
        verbose_name = "استان"

    def __str__(self):
        return self.name


class CityModel(models.Model):
    state = models.ForeignKey('StateModel', related_name='CityModel', on_delete=models.CASCADE, verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    class Meta:
        verbose_name_plural = "شهر ها"
        verbose_name = "شهر"

    def __str__(self):
        return self.name


class BillboardAttributeModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام ویژگی بیلبورد")

    class Meta:
        verbose_name_plural = "ویژگی های بیلبورد"
        verbose_name = "ویژگی بیلبورد"

    def __str__(self):
        return self.name


class BillboardManager(models.Manager):

    def by_reseller(self, request, *args, **kwargs):
        if request.user.user_group == UserModel.ADMIN_USER:
            return super().get_queryset(*args, **kwargs)
        else:
            return super().get_queryset(*args, **kwargs).filter(reseller=request.user)


class BillboardModel(models.Model):
    city = models.ForeignKey('CityModel', related_name='BillboardModel', on_delete=models.SET_NULL,
                             verbose_name="شهر", null=True)
    name = models.CharField(max_length=100, verbose_name="نام بیلبورد")
    address = models.CharField(max_length=250, verbose_name="محل بیلبورد")
    attribute = models.ManyToManyField(BillboardAttributeModel,
                                       verbose_name="ویژگی های بیلبورد", blank=True, null=True)
    description = models.TextField(verbose_name='توضیحات بیلبورد', blank=True)

    has_power = models.BooleanField(verbose_name="برق دارد؟", default=False)
    billboard_length = models.PositiveSmallIntegerField(verbose_name="طول بیلبورد")
    billboard_width = models.PositiveSmallIntegerField(verbose_name="عرض بیلبورد")

    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    reservation_date = jmodels.jDateField(verbose_name="قابل اجاره در", null=True)
    reseller = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name="نماینده", blank=True, null=True)

    map_iframe = models.TextField(verbose_name='نقشه', blank=True, null=True)
    billboard_pic = models.ImageField(upload_to=billboard_path, verbose_name="تصویر اصلی بیلبورد",
                                      blank=True, null=True)

    # SEO fields
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه", blank=True)
    url = models.SlugField(max_length=255, verbose_name='آدرس صفحه', allow_unicode=True, blank=True)
    desc = models.TextField(max_length=160, verbose_name='توضیحات صفحه', blank=True)

    # manager
    object = BillboardManager()

    class Meta:
        verbose_name_plural = "بیلبورد ها"
        verbose_name = "بیلبورد"

    def __str__(self):
        return self.name

    @classmethod
    def get_recent(cls, number: int, only: list):
        """Return of newest object the number of "number"

        ...

        Parameters
        ----------
        number : int
            the number of object to returned

        only : list
            list of the field in the model that you want to be return
            like: only=['name', 'price', ... ]

        Returns
        -------
        return a  QuerySet[BillboardModel] by number of 'number'

        """
        return cls.object.all()[:number].only(*only)

    @property
    def billboard_pic_url(self):
        """Get picture form model if picture is null change by default picture
        you can use it in template
        """
        if self.billboard_pic and hasattr(self.billboard_pic, 'url'):
            return self.billboard_pic.url
        else:
            return static('template/images/no-image.png')




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

        except AttributeError :
            name = "حذف شده"

        return name


class BillboardImageModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان عکس", blank=True)
    image = models.ImageField(upload_to=billboard_path, verbose_name="عکس")  # TODO: delete file when delete model
    billboard = models.ForeignKey(BillboardModel, related_name="BillboardImageModel",
                                  verbose_name="تصویر بیلبورد",  on_delete=models.CASCADE, null=True)
    uploader = models.ForeignKey(UserModel, related_name="BillboardImageModel",
                                 verbose_name="آپلود کننده", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "عکس های بیلبورد"
        verbose_name = "عکس بیلبورد"

    def __str__(self):
        return self.title
