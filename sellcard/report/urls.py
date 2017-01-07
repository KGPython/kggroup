#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    #卡报表（售/换/借/补/领/入库等）
    url('^report/card/',include('sellcard.report.card.urls')),
    #卷报表
    url('^report/voucher/', include('sellcard.report.voucher.urls'))
]