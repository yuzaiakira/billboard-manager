from django.urls import path, include

from account import views
from addlist.views import WatchList, PrintPDF

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(next_page='login'), name='logout'),
    path('list/', include([
      path('', WatchList.as_view(),name='WatchList'),
      path('pdf', PrintPDF.as_view(),name='get-pdf'),

    ])),
]
