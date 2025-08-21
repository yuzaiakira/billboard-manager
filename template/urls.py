from django.urls import path, re_path
from . import views
from addlist.views import AddToList, RemoveFromList
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    # path('<slug>/', views.BillboardDetail.as_view(), name='billboard-detail'),
    # path('<int:pk>/', views.BillboardDetail.as_view(), name='billboard-detail'),
    path('billboards', views.BillboardList.as_view(), name='billboard-list'),
    path('state/<slug>', views.BillboardStateList.as_view(), name='billboard-state-list'),
    path('city/<slug>', views.BillboardCityList.as_view(), name='billboard-city-list'),
    # path('state/<int:pk>', views.BillboardStateList.as_view(), name='billboard-state-list'),
    # path('city/<int:pk>', views.BillboardCityList.as_view(), name='billboard-city-list'),
    path('add-to-list/<int:pk>', AddToList.as_view(), name="add-to-list"),
    path('remove-from-list/<int:pk>', RemoveFromList.as_view(), name="remove-from-list"),
    path('search', views.BillboardSearch.as_view(), name="search"),
    re_path(r'^(?P<slug>[^/]+)/?$', views.BillboardDetail.as_view(), name='billboard-detail'),
]
