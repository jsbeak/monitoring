from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
import random
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
    pro_domain    = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        cache.delete(settings.PROJECT_DOMAIN_CACHE_KEY)  
        super().save(*args, **kwargs)  # 실제 save() 를 호출 
        
    def update(self, *args, **kwargs):
        cache.delete(settings.PROJECT_DOMAIN_CACHE_KEY)  
        super().update(*args, **kwargs)  
        
    def delete(self, *args, **kwargs):
        cache.delete(settings.PROJECT_DOMAIN_CACHE_KEY)  
        super().delete(*args, **kwargs)
       


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


# Memory 정보
class MemoryInfo( models.Model):
    memory_no = models.AutoField(primary_key=True)
    memory_server_no = models.ForeignKey("ServerInfo" , db_column="memory_server_no", related_name="memory_server_no" , on_delete=models.CASCADE , null=True )
    memory_usage  = models.IntegerField(default=0)
    memory_idle   = models.IntegerField(default=0)
    memory_create_dt  = models.DateTimeField(default=timezone.now)


# HDD 정보
class HddInfo( models.Model ):
    hdd_no = models.AutoField(primary_key=True)
    hdd_server_no = models.ForeignKey("ServerInfo" , db_column="hdd_server_no", related_name="hdd_server_no" , on_delete=models.CASCADE , null=True )
    hdd_usage = models.IntegerField(default=0)
    hdd_idle  = models.IntegerField(default=0)
    hdd_create_dt = models.DateTimeField(default=timezone.now)



# 도메인 라이센스 체크
class DomainInfo( models.Model ):
    dl_no       = models.AutoField(primary_key=True)
    dl_referer  = models.CharField(max_length=255, null=False , blank=False)
    dl_agent    = models.CharField(max_length=255, null=True , blank=True)    
    dl_host     = models.CharField(max_length=255, null=False , blank=False , default='NONE' )
    dl_ip       = models.CharField(max_length=255, null=True , blank=True)    
    dl_confirm   = models.CharField(max_length=1, null=False,  blank=False, default='N')     
    dl_create_dt = models.DateTimeField(default=timezone.now)
    


# 환경설정

def random_string():
    return str(random.randint(10000, 99999))

def config_default():
    return {}

class Config( models.Model ):
    con_no   = models.AutoField(primary_key=True)
    con_id   = models.CharField(max_length=120 , null=False , blank=False, default='')
    con_desc = models.CharField(max_length=255 , null=True , blank=True)
    con_data = models.CharField(max_length=255 , null=False , blank=False , default='')
    con_update_dt = models.DateTimeField(default=timezone.now)
