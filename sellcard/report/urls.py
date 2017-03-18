#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    #卡报表（售/换/借/补/领/入库等）
    url('^report/card/',include('sellcard.report.card.urls')),
    #券报表
    url('^report/voucher/', include('sellcard.report.voucher.urls')),
    #财务报表
    url('^report/finance/', include('sellcard.report.finance.urls'))
]