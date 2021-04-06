from django.shortcuts import render
from django.utils import timezone
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


from .models import ProjectInfo
from .models import ServerInfo
from .models import CpuInfo
from .models import MemoryInfo
from .models import HddInfo

# Create your views here.


# 요청(request) 을 넘겨받아 render 메서드를 호출하고 
# jwmonitor/main.html 템플릿을 보여준다.
def main(reqeust):
    #쿼리셋
    projects = ProjectInfo.objects.order_by('pro_no')
    return render(reqeust, 'jwmonitor/main.html' ,{'projects' : projects})


# 크롤링 agent 에서 크롤링할 프로젝트 목록 정보 요청
def api(reqeust):
    # 쿼리셋 to json 
    projects = ProjectInfo.objects.order_by('pro_no')
    #projects = ProjectInfo.objects.all()
    projects_json = serializers.serialize('json', projects)
    #return render(reqeust, 'jwmonitor/api.html' ,{'projects' : projects})
    return HttpResponse(projects_json, content_type="application/json")

#CSRF_TOKEN 비활성화
# 크롤링 agent 에서 보낸 정보를 DB 에 insert / update 
# 대상 테이블 : ServerInfo	
# update_or_create 검색 후 사용 
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