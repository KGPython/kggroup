#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    #登陆模块
    url(r'^sellcard/loginpage/', 'sellcard.login.index',name="login_index"),
    url(r'^sellcard/login/', 'sellcard.login.login',name="login"),
    url(r'^sellcard/logout/', 'sellcard.login.logout',name="logout"),
    url(r'^sellcard/vcode/', 'sellcard.login.vcode',name="vcode"),
    url(r'^sellcard/index/$', 'sellcard.views.index',name="front_index"),
    url(r'^sellcard/updatepwd/$', 'sellcard.login.updatePwd',name="updatePwd"),
    #卡操作（售/换/借/补/领/入库等）
    url('^sellcard/',include('sellcard.fornt.urls')),
    #报表相关
    url('^sellcard/',include('sellcard.report.urls'))
]