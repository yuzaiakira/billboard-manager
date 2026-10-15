from account.models import BrandModel, CompanyModel, UserModel
from billboard.models import BillboardModel, CityModel, StateModel


def make_user(username='user', password='pass12345', user_group=UserModel.NORMAL_USER, **kwargs):
    return UserModel.objects.create_user(
        username=username,
        password=password,
        user_group=user_group,
        **kwargs,
    )


def make_admin(username='admin', password='pass12345', **kwargs):
    return make_user(
        username=username,
        password=password,
        user_group=UserModel.ADMIN_USER,
        is_staff=True,
        is_superuser=True,
        **kwargs,
    )


def make_reseller(username='reseller', password='pass12345', **kwargs):
    return make_user(
        username=username,
        password=password,
        user_group=UserModel.RESELLER_USER,
        is_staff=True,
        **kwargs,
    )


def make_company(name='Test Co', **kwargs):
    return CompanyModel.objects.create(name=name, **kwargs)


def make_brand(user=None, brand_name='Brand', **kwargs):
    if user is None:
        user = make_user(username='brand_user')
    return BrandModel.objects.create(user=user, brand_name=brand_name, **kwargs)


def make_state(name='Tehran', **kwargs):
    return StateModel.objects.create(name=name, **kwargs)


def make_city(state=None, name='Tehran City', **kwargs):
    if state is None:
        state = make_state()
    return CityModel.objects.create(state=state, name=name, **kwargs)


def make_billboard(
    city=None,
    reseller=None,
    name='Billboard',
    price=1000,
    billboard_status=BillboardModel.BillboardStatus.PUBLIC,
    **kwargs,
):
    if city is None:
        city = make_city()
    defaults = {
        'city': city,
        'reseller': reseller,
        'name': name,
        'address': kwargs.pop('address', 'Addr'),
        'has_power': kwargs.pop('has_power', True),
        'billboard_length': kwargs.pop('billboard_length', 10),
        'billboard_width': kwargs.pop('billboard_width', 5),
        'price': price,
        'billboard_status': billboard_status,
    }
    defaults.update(kwargs)
    return BillboardModel.objects.create(**defaults)
