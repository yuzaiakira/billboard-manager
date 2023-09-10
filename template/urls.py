from django.urls import path
from . import views
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<int:pk>/', views.BillboardDetail.as_view(), name='billboard-detail-id'),
    path('<slug>/', views.BillboardDetail.as_view(), name='billboard-detail'),
    path('list', views.BillboardList.as_view(), name='billboard-list')
]
