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

    #售卡返回明细
    url(r'^sellcard/cardsale/orderInfo/','sellcard.fornt.cardSale.card.info',name='cardsSaleOrderInfo'),

    #大宗赠卡
    url(r'^sellcard/bestowed/$', 'sellcard.fornt.cardSale.bestowed.index',name='bestowed'),
    url(r'^sellcard/bestowed/save', 'sellcard.fornt.cardSale.bestowed.saveOrder',name='bestowedSave'),

    #赊销管理
    url(r'^sellcard/nopay/$', 'sellcard.fornt.cardSale.nopay.index',name='nopay'),



    #换卡
    url(r'^sellcard/cardchange/$', 'sellcard.fornt.cardChange.card.index', name='cardchange'),
    url(r'^sellcard/cardchange/save', 'sellcard.fornt.cardChange.card.save', name='cardchange_save'),
    url(r'^sellcard/cardschange/$', 'sellcard.fornt.cardChange.cards.index', name='cardsChange'),
    url(r'^sellcard/cardschange/query', 'sellcard.fornt.cardChange.cards.query', name='cardsChangeQuery'),

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
    #卡调拨
    url(r'^sellcard/cardmanage/cardallocation/', 'sellcard.fornt.cardManage.cardAllocation.index',name='cardAllocation'),
    url(r'^sellcard/cardmanage/allocationsave/', 'sellcard.fornt.cardManage.cardAllocation.allocationSave',name='allocationSave'),

    ###借卡管理
    #借卡
    url(r'^sellcard/borrow/sale/index/', 'sellcard.fornt.cardBorrow.sale.index',name='borrowSale'),
    url(r'^sellcard/borrow/sale/save/', 'sellcard.fornt.cardBorrow.sale.save',name='borrowSaleSave'),
    url(r'^sellcard/borrow/sale/info/', 'sellcard.fornt.cardBorrow.sale.info',name='borrowSaleInfo'),

    #退卡
    url(r'^sellcard/borrow/back/index/', 'sellcard.fornt.cardBorrow.back.index',name='borrowBack'),
    url(r'^sellcard/borrow/back/query/', 'sellcard.fornt.cardBorrow.back.query',name='borrowBackQuery'),
    url(r'^sellcard/borrow/back/save/', 'sellcard.fornt.cardBorrow.back.save',name='borrowBackSave'),
    #结算
    url(r'^sellcard/borrow/pay/index/', 'sellcard.fornt.cardBorrow.pay.index',name='borrowPay'),
    url(r'^sellcard/borrow/pay/save/', 'sellcard.fornt.cardBorrow.pay.save',name='borrowPaySave'),

    ###门店领卡(信息中心发卡)
    url(r'^sellcard/cardSent/$', 'sellcard.fornt.cardSent.view.index',name='cardSent'),
    url(r'^sellcard/cardSent/save', 'sellcard.fornt.cardSent.view.sentOrderSave',name='sentOrderSave'),
    #单据盘点
    url('^sellcard/cardSentCheck/','sellcard.fornt.cardSent.view.sentCardCheck',name='sentCardCheck'),
    url('^sellcard/cardSentOrder','sellcard.fornt.cardSent.view.sentCardOrder',name='cardSentOrder'),

    #盘点管理
    #库存盘点--卡类型
    url(r'^sellcard/check/finance/$', 'sellcard.fornt.checkManage.finance.index',name="financeCheck"),
    url(r'^sellcard/check/finance/cardtype/$', 'sellcard.fornt.checkManage.finance.cardType',name="financeCardType"),
    url(r'^sellcard/check/finance/cardinfo/$', 'sellcard.fornt.checkManage.finance.cardInfo',name="financeCardInfo"),
    #门店销售汇总
    url(r'^sellcard/check/shopsale/$', 'sellcard.fornt.checkManage.sale.index',name="shopSaleCheck"),
    url(r'^sellcard/check/shopsale/info/', 'sellcard.fornt.checkManage.sale.index',name="shopSaleInfoCheck"),
    #支付汇总
    url(r'^sellcard/check/pay/$', 'sellcard.fornt.checkManage.pay.index',name="payCheck"),
    #销售明细查询
    url(r'^sellcard/check/salequery/$', 'sellcard.fornt.checkManage.saleQuery.index', name="saleQuery"),
    url(r'^sellcard/check/salequerySell/$', 'sellcard.fornt.checkManage.saleQuerySell.index', name="saleQuerySell"),


    ###返点折扣授权码
    #生成
    url(r'^sellcard/discode/create/$', 'sellcard.fornt.disCode.create.index',name="disCodeCreate"),
    #分配
    url(r'^sellcard/discode/assign/$', 'sellcard.fornt.disCode.assign.index',name="disCodeAssign"),

    #qixu 2016-10-18 add begin
    ###报表查询分析
    # 日结销量查询
    url(r'^sellcard/analysis/dailySales/$', 'sellcard.fornt.Analysis.dailySales.index', name="dailySales"),
    #qixu 2016-10-18 add end

    #登陆模块
    url(r'^sellcard/loginpage/', 'sellcard.login.index',name="login_index"),
    url(r'^sellcard/login/', 'sellcard.login.login',name="login"),
    url(r'^sellcard/logout/', 'sellcard.login.logout',name="logout"),
    url(r'^sellcard/vcode/', 'sellcard.login.vcode',name="vcode"),
    url(r'^sellcard/admin/index/', 'sellcard.admin.views.index',name="admin_index"),
    url(r'^sellcard/index/$', 'sellcard.views.index',name="front_index"),

    url(r'^sellcard/updatepwd/$', 'sellcard.login.updatePwd',name="updatePwd"),


    #卡校验
    url(r'^sellcard/cardcheck/$', 'sellcard.common.Method.cardCheck',name='cardcheck'),
    url(r'^sellcard/cardcheck2/', 'sellcard.common.Method.cardCheck_Mssql', name='cardcheck_mssql'),
    url(r'^sellcard/cardcheck3/', 'sellcard.common.Method.cardCheck_Change', name='cardcheck_change'),
    #兑换码校验
    url(r'^sellcard/changcodecheck/', 'sellcard.common.Method.changeCodeCheck',name='changeCodeCheck'),
    #折扣修改授权码校验
    url(r'^sellcard/discodecheck/', 'sellcard.common.Method.disCodeCheck',name='disCodeCheck'),
    #更新赊销状态
    url(r'^sellcard/nopay/update', 'sellcard.common.Method.upNoPayStatus',name='upNoPayStatus'),
    #订单明细
    url(r'^sellcard/orderdetail', 'sellcard.common.Method.orderDetail',name='orderDetail'),

    # url(r'^test/','sellcard.tests.executeTest')
]