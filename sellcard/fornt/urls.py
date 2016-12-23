#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [

    #卡
    url('^sellcard/fornt/',include('sellcard.fornt.card.urls')),
    #卷
    url('^sellcard/fornt/',include('sellcard.fornt.voucherManage.urls'))
]