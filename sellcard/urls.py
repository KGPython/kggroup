#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    url(r'^sellcard/cardsale/','sellcard.fornt.cardSale.view.index'),
    url(r'^sellcard/cardssale/','sellcard.fornt.cardsSale.view.index'),
    url(r'^sellcard/cardchange/','sellcard.fornt.cardChange.view.index'),
    url(r'^sellcard/cardfill/','sellcard.fornt.cardFill.view.index'),
    url(r'^sellcard/queryfill/','sellcard.fornt.bulkSale.view.queryFill'),
    url(r'^sellcard/bulksale/','sellcard.fornt.bulkSale.view.index'),
    url(r'^sellcard/cardsent/', 'sellcard.fornt.cardSent.view.index'),
]