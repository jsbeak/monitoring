from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='dashboard'),

    # 크롤링할 프로젝트 정보 반환 
    path('craw_info/', views.craw_info  ),
    #path('api_test/', views.api_test  ),

    # 크롤링 데이터 insert 
    path('dataInsert', views.dataInsert ),       
    
    # 라이센스 체크 
    path('jiniImg', views.jiniImg ),       

    # 대시보드 클라이언트 커넥션 정보 ajax
    path('get_project' , views.get_project, name="get_project")  ,
    path('get_client_status' , views.get_client_status, name="get_client_status")  
]
