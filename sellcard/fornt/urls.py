#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [

    #卡
    url('^fornt/',include('sellcard.fornt.card.urls')),
    #卷
    url('^fornt/',include('sellcard.fornt.voucher.urls'))
]