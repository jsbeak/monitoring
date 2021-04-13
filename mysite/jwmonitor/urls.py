from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('api/', views.api  ),
    path('api_test/', views.api_test  ),
    path('dataInsert', views.dataInsert ),       
    path('jiniImg', views.jiniImg ),       
    
]
