#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    #单卡售卡
    url(r'^sellcard/cardsale/$','sellcard.fornt.cardSale.view.index',name='cardsale'),
    #单卡和批量售卡的订单保存
    url(r'^sellcard/cardsale/saveorder','sellcard.fornt.cardSale.view.saveOrder',name='saveorder'),
    #批量售卡
    url(r'^sellcard/cardssale/$','sellcard.fornt.cardsSale.view.index',name='cardssale'),
    url(r'^sellcard/cardssale/query','sellcard.fornt.cardsSale.view.query',name='cardsSaleQuery'),
    #大宗赠卡
    url(r'^sellcard/bestowed/$', 'sellcard.fornt.bestowed.view.index',name='bestowed'),
    url(r'^sellcard/bestowed/save', 'sellcard.fornt.bestowed.view.saveOrder',name='bestowedSave'),

    #换卡
    url(r'^sellcard/cardchange/$', 'sellcard.fornt.cardChange.view.index', name='cardchange'),
    url(r'^sellcard/cardchange/save', 'sellcard.fornt.cardChange.view.save', name='cardchange_save'),

    #补卡
    url(r'^sellcard/cardfill/index/','sellcard.fornt.cardFill.view.index',name='cardfill_index'),
    url(r'^sellcard/cardfill/save', 'sellcard.fornt.cardFill.view.save', name='cardfill_save'),
    url(r'^sellcard/cardfill/query/','sellcard.fornt.cardFill.view.query',name='cardfill_query'),
    url(r'^sellcard/cardfill/gocard/','sellcard.fornt.cardFill.view.gotcard',name='cardfill_gotcard'),
    url(r'^sellcard/cardfill/update/','sellcard.fornt.cardFill.view.update',name='cardfill_update'),
    url(r'^sellcard/cardfill/info/','sellcard.fornt.cardFill.view.info',name='cardfill_info'),

    ###卡管理
    #入库管理
    url(r'^sellcard/cardmanage/cardinstore', 'sellcard.fornt.cardManage.view.cardInStore',name='cardInStore'),
    url(r'^sellcard/cardmanage/carddetail', 'sellcard.fornt.cardManage.view.cardDetail',name='cardDetail'),

    ###门店领卡(信息中心发卡)
    url(r'^sellcard/cardSent/$', 'sellcard.fornt.cardSent.view.index',name='cardSent'),
    url(r'^sellcard/cardSent/save', 'sellcard.fornt.cardSent.view.sentOrderSave',name='sentOrderSave'),

    #登陆模块
    url(r'^sellcard/loginpage/', 'sellcard.login.index',name="login_index"),
    url(r'^sellcard/login/', 'sellcard.login.login',name="login"),
    url(r'^sellcard/logout/', 'sellcard.login.logout',name="logout"),
    url(r'^sellcard/vcode/', 'sellcard.login.vcode',name="vcode"),

    url(r'^sellcard/admin/index/', 'sellcard.admin.views.index',name="admin_index"),
    url(r'^sellcard/index/$', 'sellcard.views.index',name="front_index"),

    #卡校验
    url(r'^sellcard/cardcheck/$', 'sellcard.common.Method.cardCheck',name='cardcheck'),
    url(r'^sellcard/cardcheck2/', 'sellcard.common.Method.cardCheck_Mssql', name='cardcheck_mssql'),
    #兑换码校验
    url(r'^sellcard/changcodecheck/', 'sellcard.common.Method.changeCodeCheck',name='changeCodeCheck'),
]