from django.urls import path
from . import views
from addlist.views import AddToList
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<int:pk>/', views.BillboardDetail.as_view(), name='billboard-detail-id'),
    path('<slug>/', views.BillboardDetail.as_view(), name='billboard-detail'),
    path('list', views.BillboardList.as_view(), name='billboard-list'),
    path('add-to-list/<int:pk>', AddToList.as_view(), name="add-to-list")
]
