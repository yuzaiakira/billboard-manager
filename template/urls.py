from django.urls import path
from . import views
from addlist.views import AddToList
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<int:pk>/', views.BillboardDetail.as_view(), name='billboard-detail-id'),
    path('<slug>/', views.BillboardDetail.as_view(), name='billboard-detail'),
    path('billboards', views.BillboardList.as_view(), name='billboard-list'),
    path('city/<slug>', views.BillboardCityList.as_view(), name='billboard-city-list'),
    path('state/<slug>', views.BillboardStateList.as_view(), name='billboard-state-list'),
    path('add-to-list/<int:pk>', AddToList.as_view(), name="add-to-list"),
    path('search', views.BillboardSearch.as_view(), name="search"),

]
