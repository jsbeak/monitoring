from django.contrib import admin
from . import models
#from .models import Config

# 모델에서 추가한 프로젝트

@admin.register( models.ProjectInfo )
class ProjectInfoAdmin(admin.ModelAdmin):
    #Admin 목록에 보여질 필드 목록
    list_display = (
        'pro_no',
        'pro_client_nm',
        'pro_client_id',
        'pro_active_yn',
        'pro_create_dt'
    )
    #목록 내에서 링크로 지정할 필드 목록 (이를 지정하지 않으면, 첫번째 필드에만 링크가 적용)
    list_display_links = (
        'pro_client_nm',
        'pro_client_id'
    )
    # 페이지 노출 개수 ( default = 100 )
    list_per_page = 15
    search_fields = ( 
        'pro_client_nm',
        'pro_client_id'
    )

@admin.register( models.Config )
class ConfigAdmin(admin.ModelAdmin):
    list_display = (
        'con_no',
        'con_id',
        'con_data',
        'con_desc',
        'con_update_dt'        
    )
    list_display_links = (
        'con_id',
        'con_data',
        'con_desc'
    )
    search_fields = ( 
        'con_desc',
        'con_id',
        'con_data'
    )
    


#admin.site.register(models.ProjectInfom , ProjectInfoAdmin)

#admin.site.register()


