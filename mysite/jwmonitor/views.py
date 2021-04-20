from django.shortcuts import render
from django.utils import timezone
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlparse

from .models import ProjectInfo
from .models import ServerInfo
from .models import CpuInfo
from .models import MemoryInfo
from .models import HddInfo
from .models import Config
from .models import DomainInfo

from django.core.cache import cache

from PIL import Image
import json
import ipaddress
import re


# 전역변수
domain_cache_key         = settings.PROJECT_DOMAIN_CACHE_KEY
domain_license_cache_key = settings.PROJECT_LICENSE_IMG_CACHE_KEY

# Create your views here.





# 요청(request) 을 넘겨받아 render 메서드를 호출하고 
# jwmonitor/dashboard/index.html 템플릿을 보여준다.
def main(reqeust):
    #쿼리셋
    projects = ProjectInfo.objects.filter(pro_active_yn='Y').order_by('pro_no')
    
    return render(reqeust, 'jwmonitor/dashboard/index.html' ,{'projects' : projects })

# 테스트용 
def api_test(reqeust):

    projects = serializers.serialize('json' ,  ProjectInfo.objects.filter(pro_active_yn='Y').order_by('pro_no') )

    
    config = serializers.serialize('json' , Config.objects.filter(con_id='craw.engine.cycle.time') )
    
    ## 아래 참고해서 또 해보자.......
    #### http://oniondev.egloos.com/9884186

    ret = dict()

    ret['projects'] =  projects 
    ret['config']   =  config 

    return JsonResponse(ret, safe=False)

######################################################
# 크롤링 agent 에서 크롤링할 프로젝트 목록 정보 요청
######################################################
def api(reqeust):
    
    config_json   = serializers.serialize('json', Config.objects.filter(con_id='craw.engine.cycle.time') ) 
    projects_json = serializers.serialize('json', ProjectInfo.objects.filter(pro_active_yn='Y').order_by('pro_no') )

    result = {
       'projects' : projects_json,
       'config'   : config_json
    }

    #JSON 인코딩
    result_json = json.dumps(result)

    #print( result )
    

    return HttpResponse( result_json , content_type="application/json")


    

######################################################
# 도메인 라이센스 검사 
######################################################
def jiniImg(request):

    # 도메인 체크 ( 설정에 의해 체크 주기 설정을 추가해줘야함 )
    check_domain(request) 

    # Cache 기능
    # https://somnusnote.tistory.com/entry/Django%EC%9D%98-cache-%EC%82%AC%EC%9A%A9

    # 1px 이미지 리턴 
    return get_check_img()


        

######################################################
##  허용된 도메인인지 체크
##  - IP 로 찍히는건 Pass 
######################################################
def check_domain(request):
    

    try:
        #-------------------------------------------
        # 요청 referer 검사
        #-------------------------------------------
        user_agent = request.META.get('HTTP_USER_AGENT')
        referer = request.META.get('HTTP_REFERER', '')
        client_ip =  get_client_ip(request)         
        client_domain = urlparse(referer).hostname

        # IP 주소나 로컬호스트 일경우    
        if check_ip_address(client_domain):
            #print("아이피 주소입니다. 라이센스 체크를 진행하지 않습니다.")
            return
        if  client_domain in ['localhost' , '127.0.0.1'] :
            #print("로컬호스트 주소입니다. 라이센스 체크를 진행하지 않습니다.")
            return
        
        # 검사했던 도메인인지 체크 
        #checkConfirmDomainList(request)
        # 등록된 전체 도메인 리스트를 가져온다.
        if not cache.get(domain_cache_key):

            domain_list = []    
            porjectInfoList = ProjectInfo.objects.filter(pro_active_yn='Y', pro_domain__isnull=False).only('pro_domain')
            
            for projectInfo in porjectInfoList:
                
                for domain in projectInfo.pro_domain.split(','):
                    # *.sample.com 에서 '*.' 을 제거하고 리스트업  
                    domain = domain.replace('*.','')  
                    domain_list.append(domain )
                    
            # 전체 도메인 캐시에 저장        
            cache.set(domain_cache_key, domain_list)
            #print( domain_list )

        # 등록된 허용 도메인 리스트 # ['localhost', 'cafe24.com', 'jsbeak.cafe24.com']
        confirm_domain_list = cache.get(domain_cache_key)
        
        # 허용된 도메인리스트에 포함되지 않으면 데이터 등록
        if client_domain not in confirm_domain_list:
        
            ## 디비에 존재하지 않으면 넣고 .. 전체 리스트를 다시 캐시에 담고 -> 인서트하면 캐시 삭제하고? 
            domainCount = DomainInfo.objects.filter(dl_host=client_domain, dl_confirm='N').count()

            if( domainCount == 0 ):
                # 등록된 도메인 값이 없다면 넣어준다.
                doaminInfo = DomainInfo(
                    dl_referer = referer,
                    dl_agent = user_agent,
                    dl_host = client_domain,
                    dl_ip = client_ip
                )
                doaminInfo.save()

        print( '-------------------------------------------' )
        print( 'AGENT : '  +  user_agent )
        print( 'CLIENT_IP '  + client_ip )
        print( 'Referer '  + referer )
        print( '허용 도메인 목록 : '  + str(confirm_domain_list)  )
        print( '클라이언트 도메인 : '  +  client_domain ) # 포트 제거 , * 제거 
        print( '-------------------------------------------' )
    
    
    except Exception as e:
        print(e)
        



    

    


######################################################
#CSRF_TOKEN 비활성화
# 크롤링 agent 에서 보낸 정보를 DB 에 insert / update 
######################################################
@csrf_exempt
def dataInsert(request):


    ####################################
    # 서버 정보  
    ####################################
    server_os = request.POST['server.os']
    server_was          = request.POST['server.was']
    server_was_path     = request.POST['server.was.path']
    server_start_time   = request.POST['server.start.time']
    server_java_home    = request.POST['server.java.home']
    server_java_version = request.POST['server.java.version']
    server_pro_no       = request.POST['pro.no']
    server_hdd_total    = request.POST['server.hdd.total']
    server_memory_total = request.POST['server.memory.total']
    server_db_type      = request.POST['server.db.type']    


    # ServerInfo 객체 생성
    serverInfo = ServerInfo( 
        server_os=server_os,
        server_was=server_was,
        server_was_path=server_was_path,
        server_start_time=server_start_time,
        server_java_home=server_java_home,
        server_java_version=server_java_version,
        #pro_no=pro_no,
        server_pro_no = ProjectInfo.objects.get(pro_no=server_pro_no ), # 외래키는 객체로 넘겨줘야 
        server_hdd_total=server_hdd_total,
        server_memory_total=server_memory_total,
        server_db_type=server_db_type    
    )


    ####################################
    # CPU 정보
    ####################################
    cpu_usage = request.POST['cpu.usage']
    cpu_idle  = request.POST['cpu.idle']

    # CPU 객체 생성
    cpuInfo = CpuInfo(
        cpu_usage = cpu_usage,
        cpu_idle  = cpu_idle
    )

    ####################################
    # 메모리 정보
    ####################################
    memory_usage = request.POST['memory.usage']
    memory_idle  = request.POST['memory.idle']
    
    memoryInfo = MemoryInfo(
        memory_usage    =   memory_usage,
        memory_idle     =   memory_idle
    )


    ####################################
    # 하드디스크 정보
    ####################################
    hdd_usage = request.POST['hdd.usage']
    hdd_idle  = request.POST['hdd.idle']
    
    hddInfo = HddInfo(
        hdd_usage   =   hdd_usage,
        hdd_idle    =   hdd_idle
    )



    if server_pro_no is None:
        return
    
    # 트렌잭션
    with transaction.atomic(): 
        
        ####################################
        # 서버정보 등록
        ####################################
        try:
            
            serverObj = ServerInfo.objects.get(server_pro_no=server_pro_no)

            serverObj.server_os=server_os
            serverObj.server_was=server_was
            serverObj.server_was_path=server_was_path
            serverObj.server_start_time=server_start_time
            serverObj.server_java_home=server_java_home
            serverObj.server_java_version=server_java_version
            serverObj.server_pro_no = serverInfo.server_pro_no
            serverObj.server_hdd_total= server_hdd_total
            serverObj.server_memory_total=server_memory_total
            serverObj.server_db_type=server_db_type

            serverObj.save()

            ## -------------------------------------    
            ## 참조테이블 FK 정보     
            ## -------------------------------------
            cpuInfo.cpu_server_no       = ServerInfo.objects.get(server_no=serverObj.server_no)
            memoryInfo.memory_server_no = ServerInfo.objects.get(server_no=serverObj.server_no)
            hddInfo.hdd_server_no       = ServerInfo.objects.get(server_no=serverObj.server_no)

        except ServerInfo.DoesNotExist: # 등록된 정보가 존재하지 않는 경우

            serverInfo.save()
            
            ## -------------------------------------    
            ## 참조테이블 FK 정보     
            ## -------------------------------------
            cpuInfo.cpu_server_no       = ServerInfo.objects.get(server_no=serverInfo.server_no)
            memoryInfo.memory_server_no = ServerInfo.objects.get(server_no=serverInfo.server_no)
            hddInfo.hdd_server_no       = ServerInfo.objects.get(server_no=serverInfo.server_no)

        ####################################
        # CPU 정보 등록
        ####################################
        try:
            
            if cpuInfo.cpu_server_no is None:
                return


            cpuInfo.save()

        except:
            print("Cpu Info Insert Error !!")


        ####################################
        # 메모리 정보 등록
        ####################################
        try:
            if memoryInfo.memory_server_no is None:
                return    

            memoryInfo.save()
                
        except:        
            print("Memory Info Insert Error !!")


        
        ####################################
        # HDD 정보 등록
        ####################################
        try:

            if hddInfo.hdd_server_no is None:
                return

            hddInfo.save()
                
        except:        
            print("HDD Info Insert Error !!")        


    return HttpResponse(True)



## **********************************************************************************
## Util Method 
## **********************************************************************************

######################################################
# 클라이언트 아이피 리턴
######################################################
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

######################################################
# 1px 투명이미지 생성
######################################################
def get_check_img():

    if not cache.get(domain_license_cache_key):

        img = Image.new('RGBA', (1, 1), (0, 0, 0, 1))
        response = HttpResponse(content_type="image/png")
        img.save(response, "png")

        cache.set(domain_license_cache_key , response )
        
    else:
        
        response = cache.get( domain_license_cache_key )
    
    return response

######################################################
# 아이피 주소인지 체크
######################################################
def check_ip_address(domain):

    try:
        # 포트번호 제거     
        #remove_port_ip = re.match('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', domain)
        #if remove_port_ip:
        #    domain = remove_port_ip[0]
        
        ip = ipaddress.ip_address(domain)

        return True

    except ValueError:
        return False

