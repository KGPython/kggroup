__author__ = 'qixu'
from django.conf.urls import url
urlpatterns = [
    #=================================用户管理 bgein============================
    #列表
    url(r'^user/$', 'sellcard.system.used.index', name="userManageList"),
    #新建/修改（get）
    url(r'^user/detail/$', 'sellcard.system.used.detail', name="userManageDetail"),
    #保存（post）
    url(r'^user/save/$', 'sellcard.system.used.save', name="userManageSave"),
    #=================================用户管理 end==============================
]