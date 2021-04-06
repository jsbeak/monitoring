from django.db import models
from django.utils import timezone
# Create your models here.


# 모델 만들기 
# 모델 작성 후 python manage.py makemigrations jwmonitor 명령어를 통해 데이터베이스에 모델을 반영할 수 있다. 

## 모델 작성 후 
## python manage.py makemigrations jwmonitor
## python manage.py migrate jwmonitor


## database is Lock 에러 발생시 
## https://kwonsoonwoo.github.io/sql/2018/10/08/Database-is-locked-%EC%97%90%EB%9F%AC.html

# 프로젝트 정보 모델
class ProjectInfo( models.Model):

    SELECT_OPTION = {
        ('Y' , 'Y'),
        ('N' , 'N')
    }

    pro_no  = models.AutoField(primary_key=True)
    pro_client_id = models.CharField(max_length=60, null=False , blank=False)
    pro_client_nm = models.CharField(max_length=60, null=False , blank=False)
    pro_active_yn = models.CharField(max_length=1 , choices=SELECT_OPTION, default="Y")
    pro_url       = models.CharField(max_length=250 , null=True , blank=True )
    pro_craw_url  = models.CharField(max_length=250 , null=True , blank=True )
    pro_create_dt = models.DateTimeField(default=timezone.now)



# 서버정보
# 외래키 ( 참조할 테이블 , 개체관계에서 사용할 이름 , 개체 삭제시 수행할 동작 )

class ServerInfo( models.Model):
    server_no  = models.AutoField(primary_key=True)
    server_os  = models.CharField(max_length=120 , null=True , blank=True)
    server_was = models.CharField(max_length=120 , null=True , blank=True)
    server_was_path = models.CharField(max_length=250 , null=True , blank=True)
    server_start_time = models.CharField(max_length=120,null=True , blank=True)
    server_java_home = models.CharField(max_length=250, null=True , blank=True)
    server_java_version  = models.CharField(max_length=60, null=True , blank=True)
    server_pro_no = models.ForeignKey("ProjectInfo" , db_column="server_pro_no" , related_name="server_pro_no", on_delete=models.CASCADE , null=True )
    server_hdd_total  = models.IntegerField(default=0 )
    server_memory_total = models.IntegerField(default=0 )
    server_db_type = models.CharField(max_length=120 , null=True , blank=True)
    server_create_dt = models.DateTimeField(default=timezone.now)
    #server_db_url  = models.CharField(max_length=250)      



# CPU 정보
class CpuInfo( models.Model ):
    cpu_no = models.AutoField(primary_key=True)
    cpu_server_no = models.ForeignKey("ServerInfo" , db_column="cpu_server_no", related_name="cpu_server_no" , on_delete=models.CASCADE , null=True )
    cpu_usage = models.IntegerField(default=0)
    cpu_idle  = models.IntegerField(default=0)
    cpu_create_dt = models.DateTimeField(default=timezone.now)