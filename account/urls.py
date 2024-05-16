from django.urls import path, include

from account import views
from addlist.views import WatchList, RemoveList, PrintPDF, ExportExcel

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(next_page='login'), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('list/', include([
      path('', WatchList.as_view(),name='WatchList'),
      path('remove-list', RemoveList.as_view(),name='remove-list'),
      path('pdf', PrintPDF.as_view(),name='get-pdf'),
      path('excel', ExportExcel.as_view(),name='get-excel'),

    ])),
]
