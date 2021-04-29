from django.shortcuts import render
from django.utils import timezone
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required

from .models import ProjectInfo
from .models import ServerInfo
from .models import CpuInfo
from .models import MemoryInfo
from .models import HddInfo
from .models import Config
from .models import DomainInfo
from django.db.models import F

from django.core.cache import cache
from django.db.models import Max
from datetime import datetime
from PIL import Image
import json
import ipaddress
import re
import requests
import telegram

# 전역변수
domain_cache_key         = settings.PROJECT_DOMAIN_CACHE_KEY
domain_license_cache_key = settings.PROJECT_LICENSE_IMG_CACHE_KEY

# Create your views here.




#######################################################

#   D A S H B O A R D

# 요청(request) 을 넘겨받아 render 메서드를 호출하고 
# jwmonitor/dashboard/index.html 템플릿을 보여준다.
##############################################
@login_required   #@permission_required 로 사용시 명시된 권한을 가진 사람만 접근가능
def main(reqeust):

    ## 메인 상단 카드 영역 -------------------------------------------------------------------------

    #프로젝트 수
    project_cnt = ProjectInfo.objects.filter(pro_active_yn='Y').count()
    
    # 라이센스등록 허용 도메인 수
    accepted_domain_list = get_confirm_domain_list()    

    # 미등록 도메인 수
    unacceptable_domain_cnt  =  DomainInfo.objects.filter(dl_confirm='N').count()
    
    ## End  메인 상단 카드 영역 -------------------------------------------------------------------------


    ## 서버 사용량 영역     -------------------------------------------------------------------------

    # CPU 사용량
    # select 
	# c.* from
	# jwmonitor_cpuinfo c join (
	# 	select 
	# 		cpu_server_no , max(  cpu_no	)  as  cpu_no
	# 		from jwmonitor_cpuinfo 
	# 		GROUP by cpu_server_no 
	# )  M
	# where M.cpu_no = c.cpu_no
    cpu_max_set = CpuInfo.objects.values('cpu_server_no').annotate(cpu_no=Max('cpu_no'))

    cpu_no_list = []
    for cpu in cpu_max_set:
        cpu_no_list.append(cpu['cpu_no'])

    cpu_info = CpuInfo.objects.all().values(
        'cpu_no',
        'cpu_server_no' , 
        'cpu_usage' ,
        'cpu_idle',
        server_pro_no=F('cpu_server_no__server_pro_no'), 
        client_id=F('cpu_server_no__server_pro_no__pro_client_id') 
        ).filter(cpu_no__in=cpu_no_list ).order_by('-cpu_usage')[:10][:10]
    

    ## End 서버 사용량 영역     -------------------------------------------------------------------------


    ## 메모리 사용량 영역     -------------------------------------------------------------------------
    memory_max_set = MemoryInfo.objects.values('memory_server_no').annotate(memory_no=Max('memory_no'))

    memory_no_list = []
    for mem in memory_max_set:
        memory_no_list.append(mem['memory_no'])

    memory_info = MemoryInfo.objects.all().values(
        'memory_no',
        'memory_server_no' , 
        'memory_usage' ,
        'memory_idle',
        server_pro_no=F('memory_server_no__server_pro_no'), 
        client_id=F('memory_server_no__server_pro_no__pro_client_id') 
        ).filter(memory_no__in=memory_no_list ).order_by('-memory_usage')[:10]

    ## End 메모리 사용량 영역     -------------------------------------------------------------------------

    ## HDD 사용량 영역     -------------------------------------------------------------------------
    hdd_max_set = HddInfo.objects.values('hdd_server_no').annotate(hdd_no=Max('hdd_no'))

    hdd_no_list = []
    for hdd in hdd_max_set:
        hdd_no_list.append(hdd['hdd_no'])

    hdd_info = HddInfo.objects.all().values(
        'hdd_no',
        'hdd_server_no' , 
        'hdd_usage' ,
        'hdd_idle',
        server_pro_no=F('hdd_server_no__server_pro_no'), 
        client_id=F('hdd_server_no__server_pro_no__pro_client_id') 
        ).filter(hdd_no__in=hdd_no_list ).order_by('-hdd_usage')[:10]

    ## End HDD 사용량 영역     -------------------------------------------------------------------------

    context = {
        'project_cnt': project_cnt ,
        'unacceptable_domain_cnt' : unacceptable_domain_cnt,
        'accepted_domain_cnt'   :  len(accepted_domain_list),
        'cpu_info'              : cpu_info,
        'memory_info'           : memory_info,
        'hdd_info'              : hdd_info
        }
    

    return render(reqeust, 'jwmonitor/dashboard/index.html' , context)

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
def craw_info(reqeust):
    
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
            
            
            domain_list = get_confirm_domain_list()    
            # porjectInfoList = ProjectInfo.objects.filter(pro_active_yn='Y', pro_domain__isnull=False).only('pro_domain')
            
            # for projectInfo in porjectInfoList:
                
            #     for domain in projectInfo.pro_domain.split(','):
            #         # *.sample.com 에서 '*.' 을 제거하고 리스트업  
            #         domain = domain.replace('*.','')  
            #         domain_list.append(domain )
                    
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


@csrf_exempt
@login_required()
def get_client_status(request):

    ## 클라이언트 서버 상태  ---------------------------------------------------------------------------
    
    client_host = request.POST['client_host']
    result_code = False
    timeout = 5
    time = 0 
    state = "Not connected"

    try:
	    #time = requests.get( client_host , timeout=timeout)
        time = requests.get( client_host, timeout= timeout ).elapsed.total_seconds()
        state = "Active"
    except (requests.ConnectionError, requests.Timeout) as exception:
        send_admin_alarm(client_host)
    except:
        send_admin_alarm(client_host)
    
    ## END 클라이언트 서버 상태  ---------------------------------------------------------------------------

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    context = {
            'time' : int(time * 1000) ,
            'state' : state,
            'date' : current_time
            }
    
    return HttpResponse(  json.dumps(context) , content_type="application/json")


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


######################################################
# 등록 된 허용 도메인 정보
######################################################
def get_confirm_domain_list():    
    domain_list = []    
    porjectInfoList = ProjectInfo.objects.filter(pro_active_yn='Y', pro_domain__isnull=False).only('pro_domain')
    
    for projectInfo in porjectInfoList:
        
        for domain in projectInfo.pro_domain.split(','):
            # *.sample.com 에서 '*.' 을 제거하고 리스트업  
            domain = domain.replace('*.','')  
            domain_list.append(domain )
    
    return domain_list

######################################################
# 활성화된 프로젝트 목록
######################################################            
@csrf_exempt
@login_required()
def get_project(request):
    
    projects = serializers.serialize('json' ,  ProjectInfo.objects.filter(pro_active_yn='Y').order_by('pro_no') )

    return HttpResponse( projects )


######################################################
# 관리자에게 메시지 발송 ( https://vmpo.tistory.com/85 ) 
######################################################            
def send_admin_alarm(client_host):
    
    project_info = ProjectInfo.objects.get(pro_url=client_host)

    message = project_info.pro_client_nm + '('  +  project_info.pro_url + ') 서버접속이 원할하지 않습니다. 확인이 필요합니다.' 

    telgm_token = '1728694309:AAE6PDHdX5yhLn3CtavuT74SQ_m3BkUtrNs'
    bot = telegram.Bot(token = telgm_token)

    # 대화내용 가져오기 (chat_id )
    #updates = bot.getUpdates()
    bot.sendMessage(chat_id = '286351362', text=message )

