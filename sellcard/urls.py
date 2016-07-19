#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    url(r'^sellcard/cardsale/$','sellcard.fornt.cardSale.view.index',name='cardsale'),
    url(r'^sellcard/cardsale/saveorder', 'sellcard.fornt.cardSale.view.saveOrder',name='saveorder'),

    url(r'^sellcard/cardssale/','sellcard.fornt.cardsSale.view.index',name='cardssale'),
    url(r'^sellcard/cardchange/','sellcard.fornt.cardChange.view.index',name='cardchange'),
    url(r'^sellcard/cardfill/','sellcard.fornt.cardFill.view.index',name='cardfill'),
    url(r'^sellcard/queryfill/','sellcard.fornt.bulkSale.view.queryFill',name='queryfill'),
    url(r'^sellcard/bulksale/','sellcard.fornt.bulkSale.view.index',name='bulksale'),
    url(r'^sellcard/cardsent/', 'sellcard.fornt.cardSent.view.index',name='cardsent'),

    url(r'^sellcard/cardcheck/', 'sellcard.common.Method.cardCheck',name='cardcheck'),

    url(r'^sellcard/setSn/', 'sellcard.common.Method.setOrderSn',name='setSn'),
]