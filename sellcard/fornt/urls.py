#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    url('^fornt/',include('sellcard.fornt.card.urls')),
    url('^fornt/voucher/',include('sellcard.fornt.voucher.urls')),
    url('^fornt/vip/',include('sellcard.fornt.vip.urls'))
]