import telegram
from asgiref.sync import sync_to_async
from . import views

def send_telegram_alarm(client_host , message_code ):

    try:
        #https://docs.djangoproject.com/en/3.2/topics/async/
        project_info  = sync_to_async( views.get_project_info(client_host) , thread_sensitive=True ) 
        message =  message_code  + project_info.pro_client_nm + '('  +  project_info.pro_url + ') '   

        # 봇방 토큰값 
        telgm_token = '1770667235:AAGPXFSznsGpNTe2leuPw9pBPSAxXS1xUh4'
        bot = telegram.Bot(token = telgm_token)

        # 대화내용 가져오기 (chat_id )
        #updates = bot.getUpdates()

        #bot.sendMessage(chat_id = '286351362', text=message ) # bot 방 
        #bot.sendMessage(chat_id = '@monitor_telegram', text=message ) # 채널 ( 공개일때 )
        
        ## 메시지 발송 ## 
        #bot.sendMessage(chat_id = '-1001296255544', text=message )  #  채널 ( 바공개일때 )
        

    # bot 아이디 확인 url 
    #https://api.telegram.org/bot1770667235:AAGPXFSznsGpNTe2leuPw9pBPSAxXS1xUh4/sendMessage?chat_id=@monitor_telegram&text=test

    except Exception as e:
        print(e)