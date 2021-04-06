from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('api/', views.api  ),
    path('dataInsert', views.dataInsert ),       
]
