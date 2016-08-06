#-*- coding:utf-8 -*-
from django.conf.urls import include,url
urlpatterns = [
    #单卡售卡
    url(r'^sellcard/cardsale/$','sellcard.fornt.cardSale.card.index',name='cardsale'),
    #单卡和批量售卡的订单保存
    url(r'^sellcard/cardsale/saveorder','sellcard.fornt.cardSale.card.saveOrder',name='saveorder'),
    #批量售卡
    url(r'^sellcard/cardssale/$','sellcard.fornt.cardSale.cards.index',name='cardssale'),
    url(r'^sellcard/cardssale/query','sellcard.fornt.cardSale.cards.query',name='cardsSaleQuery'),

    #大宗赠卡
    url(r'^sellcard/bestowed/$', 'sellcard.fornt.cardSale.bestowed.index',name='bestowed'),
    url(r'^sellcard/bestowed/save', 'sellcard.fornt.cardSale.bestowed.saveOrder',name='bestowedSave'),

    #欠款管理
    url(r'^sellcard/nopay/$', 'sellcard.fornt.cardSale.nopay.index',name='nopay'),
    url(r'^sellcard/nopay/detail', 'sellcard.fornt.cardSale.nopay.detail',name='nopayDetail'),

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
    url(r'^sellcard/cardmanage/cardinstore/', 'sellcard.fornt.cardManage.view.cardInStore',name='cardInStore'),
    url(r'^sellcard/cardmanage/cardallocation/', 'sellcard.fornt.cardManage.cardAllocation.index',name='cardAllocation'),


    ###门店领卡(信息中心发卡)
    url(r'^sellcard/cardSent/$', 'sellcard.fornt.cardSent.view.index',name='cardSent'),
    url(r'^sellcard/cardSent/save', 'sellcard.fornt.cardSent.view.sentOrderSave',name='sentOrderSave'),

    #盘点管理
    #财务盘点--卡类型
    url(r'^sellcard/check/finance/$', 'sellcard.fornt.checkManage.finance.index',name="financeCheck"),
    url(r'^sellcard/check/finance/cardtype/$', 'sellcard.fornt.checkManage.finance.cardType',name="financeCardType"),
    url(r'^sellcard/check/finance/cardinfo/$', 'sellcard.fornt.checkManage.finance.cardInfo',name="financeCardInfo"),
    #销售汇总
    url(r'^sellcard/check/sale/$', 'sellcard.fornt.checkManage.sale.index',name="saleCheck"),
    #支付汇总
    url(r'^sellcard/check/pay/$', 'sellcard.fornt.checkManage.pay.index',name="payCheck"),
    #销售明细查询
    url(r'^sellcard/check/salequery/$', 'sellcard.fornt.checkManage.saleQuery.index',name="saleQuery"),


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
    url(r'^sellcard/cardcheck3/', 'sellcard.common.Method.cardCheck_Change', name='cardcheck_change'),
    #兑换码校验
    url(r'^sellcard/changcodecheck/', 'sellcard.common.Method.changeCodeCheck',name='changeCodeCheck'),
    #更新欠款状态
    url(r'^sellcard/nopay/update', 'sellcard.common.Method.upNoPayStatus',name='upNoPayStatus'),


]