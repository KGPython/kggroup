#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    url(r'^sellcard/cardsale/','sellcard.fornt.cardSale.view.index',name='cardsale'),
    url(r'^sellcard/cardssale/','sellcard.fornt.cardsSale.view.index',name='cardssale'),
    url(r'^sellcard/cardchange/','sellcard.fornt.cardChange.view.index',name='cardchange'),
    #url(r'^sellcard/cardfill/','sellcard.fornt.cardFill.view.index',name='cardfill'),
    url(r'^sellcard/queryfill/','sellcard.fornt.bulkSale.view.queryFill',name='queryfill'),
    url(r'^sellcard/bulksale/','sellcard.fornt.bulkSale.view.index',name='bulksale'),
    url(r'^sellcard/cardsent/', 'sellcard.fornt.cardSent.view.index',name='cardsent'),

    url(r'^sellcard/loginpage/', 'sellcard.login.index',name="login_index"),
    url(r'^sellcard/login/', 'sellcard.login.login',name="login"),
    url(r'^sellcard/logout/', 'sellcard.login.logout',name="logout"),
    url(r'^sellcard/vcode/', 'sellcard.login.vcode',name="vcode"),

    url(r'^sellcard/admin/index/', 'sellcard.admin.views.index',name="admin_index"),
    url(r'^sellcard/index/$', 'sellcard.views.index',name="front_index"),

    url(r'^sellcard/cardcheck/', 'sellcard.common.Method.cardCheck',name='cardcheck'),

    url(r'^sellcard/setSn/', 'sellcard.common.Method.setOrderSn',name='setSn'),

    url(r'^sellcard/cardfill/index/','sellcard.fornt.cardFill.view.index',name='cardfill_index'),
    url(r'^sellcard/cardfill/query/','sellcard.fornt.cardFill.view.query',name='cardfill_query'),
]