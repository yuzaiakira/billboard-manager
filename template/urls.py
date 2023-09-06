from django.urls import path
from . import views
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<pk>/', views.BillboardDetail.as_view(), name='billboard-detail'),
]