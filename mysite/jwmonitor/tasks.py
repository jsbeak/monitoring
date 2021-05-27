from django.views.decorators.csrf import csrf_exempt
from background_task import background
from datetime import datetime
from .models import ProjectInfo
from .models import RealTimeInfo
import requests
import asyncio
from time import time
from . import push_message
from . import error_msg


## 백그라운드 실행 
## https://mrsence.tistory.com/85
## https://www.python2.net/questions-389809.htm

## 실행 방법은 
##  python manage.py process_tasks 

@csrf_exempt
@background() 
def demo_task(): 
    # now = datetime.now()
    # print('')
    # print( now )
    # print('')

    project_list = ProjectInfo.objects.filter(pro_active_yn='Y', pro_domain__isnull=False)

    async def fetch(project):

        timeout = 5
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        realtimeInfo = RealTimeInfo()
        realtimeInfo.re_pro_no = project

        try:
            # 서버 상태 체크
            response = requests.get( project.pro_craw_url  + "?jini-s=Y" , timeout= timeout )
            realtimeInfo.re_server_time = int( response.elapsed.total_seconds()  * 1000 )
            realtimeInfo.re_server_status_code = response.status_code
            #result_data['server_time'] = response.elapsed.total_seconds()
            #result_data['server_status_code'] = response.status_code


            print( response.elapsed.total_seconds()  )

            #result_data['server_time'] = requests.get( project.pro_craw_url  + "?jini-s=Y" , timeout= timeout ).elapsed.total_seconds()
            #result_data['server_state'] = "Active"
        except (requests.ConnectionError, requests.Timeout) as e:
            realtimeInfo.re_server_status_code = 408 ## 요청시간 초과
            push_message.send_telegram_alarm(project.pro_url , error_msg.HTTP_408_MSG )
        except Exception as e:
            realtimeInfo.re_server_status_code = 520 ## 알수 없음
            push_message.send_telegram_alarm(project.pro_url , e )
        

        try:
            # BASIC 디비 상태 체크
            response = requests.get( project.pro_craw_url  + "?jini-d=Y" , timeout= timeout )
            realtimeInfo.re_db_time =  int( response.elapsed.total_seconds() * 1000 ) 
            realtimeInfo.re_db_status_code = response.status_code
            
            #result_data['db_time'] = response.elapsed.total_seconds()
            #result_data['db_status_code'] = response.status_code
            
            #result_data['db_time'] = requests.get( project.pro_craw_url  + "?jini-d=Y" , timeout= timeout ).elapsed.total_seconds()
            #result_data['db_state'] = "Active"
        except (requests.ConnectionError, requests.Timeout) as exception:
            realtimeInfo.re_db_status_code = 408 ## 요청시간 초과
            push_message.send_telegram_alarm(project.pro_url , error_msg.HTTP_408_MSG )
        except Exception as e:
            realtimeInfo.re_db_status_code = 520 ## 알수없음 
            push_message.send_telegram_alarm(project.pro_url , e )

        realtimeInfo.save()


        #return result_data

        
    async def main():
        
        futures = [asyncio.ensure_future(fetch(project)) for project in project_list] # 태스크(퓨처) 객체를 리스트로 만듦
        result = await asyncio.gather(*futures)                # 결과를 한꺼번에 가져옴
        #print(result)
        return result
    
    ##########################################################
    ## 배치 시작전에 이전에 등록되 있던 배치는 모두 지우고 다시???? 
    ##########################################################

    begin = time()
    loop = asyncio.new_event_loop()          # 이벤트 루프를 얻음
    context = loop.run_until_complete(main())          # main이 끝날 때까지 기다림
    loop.close()                             # 이벤트 루프를 닫음
    end = time()

    