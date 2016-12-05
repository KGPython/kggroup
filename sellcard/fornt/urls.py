from django.conf.urls import url
urlpatterns = [
    ################################################# 售卡模块 start ##############################################
    #单卡售卡
    url(r'^fornt/cardsale/$','sellcard.fornt.cardSale.card.index',name='cardsale'),
    #单卡和批量售卡的订单保存
    url(r'^fornt/cardsale/saveorder','sellcard.fornt.cardSale.card.saveOrder',name='saveorder'),
    #批量售卡
    url(r'^fornt/cardssale/$','sellcard.fornt.cardSale.cards.index',name='cardssale'),
    url(r'^fornt/cardssale/query','sellcard.fornt.cardSale.cards.query',name='cardsSaleQuery'),

    #大宗赠卡
    url(r'^fornt/bestowed/$', 'sellcard.fornt.cardSale.bestowed.index',name='bestowed'),
    url(r'^fornt/bestowed/save', 'sellcard.fornt.cardSale.bestowed.saveOrder',name='bestowedSave'),
    ################################################# 售卡模块 end ###############################################

    ################################################# 换卡模块 start #############################################
    url(r'^fornt/cardchange/$', 'sellcard.fornt.cardChange.card.index', name='cardchange'),
    url(r'^fornt/cardchange/save', 'sellcard.fornt.cardChange.card.save', name='cardchange_save'),
    url(r'^fornt/cardschange/$', 'sellcard.fornt.cardChange.cards.index', name='cardsChange'),
    url(r'^fornt/cardschange/query', 'sellcard.fornt.cardChange.cards.query', name='cardsChangeQuery'),
    ################################################# 换卡模块 end ###############################################

    ################################################# 补卡模块 start #############################################
    url(r'^fornt/cardfill/index/','sellcard.fornt.cardFill.view.index',name='cardfill_index'),
    url(r'^fornt/cardfill/save', 'sellcard.fornt.cardFill.view.save', name='cardfill_save'),
    url(r'^fornt/cardfill/query/','sellcard.fornt.cardFill.view.query',name='cardfill_query'),
    url(r'^fornt/cardfill/gocard/','sellcard.fornt.cardFill.view.gotcard',name='cardfill_gotcard'),
    url(r'^fornt/cardfill/update/','sellcard.fornt.cardFill.view.update',name='cardfill_update'),
    url(r'^fornt/cardfill/info/','sellcard.fornt.cardFill.view.info',name='cardfill_info'),
    ################################################# 补卡模块 end ###############################################

    ################################################# 借卡模块 end ###############################################
    #借卡
    url(r'^fornt/borrow/sale/index/', 'sellcard.fornt.cardBorrow.sale.index',name='borrowSale'),
    url(r'^fornt/borrow/sale/save/', 'sellcard.fornt.cardBorrow.sale.save',name='borrowSaleSave'),
    url(r'^fornt/borrow/sale/info/', 'sellcard.fornt.cardBorrow.sale.info',name='borrowSaleInfo'),

    #退卡
    url(r'^fornt/borrow/back/index/', 'sellcard.fornt.cardBorrow.back.index',name='borrowBack'),
    url(r'^fornt/borrow/back/query/', 'sellcard.fornt.cardBorrow.back.query',name='borrowBackQuery'),
    url(r'^fornt/borrow/back/save/', 'sellcard.fornt.cardBorrow.back.save',name='borrowBackSave'),
    #结算
    url(r'^fornt/borrow/pay/index/', 'sellcard.fornt.cardBorrow.pay.index',name='borrowPay'),
    url(r'^fornt/borrow/pay/save/', 'sellcard.fornt.cardBorrow.pay.save',name='borrowPaySave'),
    ################################################# 借卡管理 end ###############################################

    ################################################# 卡管理 start ##############################################
    #领卡
    url(r'^fornt/cardSent/$', 'sellcard.fornt.cardSent.view.index',name='cardSent'),
    url(r'^fornt/cardSent/save', 'sellcard.fornt.cardSent.view.sentOrderSave',name='sentOrderSave'),
    #卡入库
    url(r'^fornt/cardmanage/cardinstore/', 'sellcard.fornt.cardManage.view.cardInStore',name='cardInStore'),
    #卡调拨
    url(r'^fornt/cardmanage/cardallocation/', 'sellcard.fornt.cardManage.cardAllocation.index',name='cardAllocation'),
    url(r'^fornt/cardmanage/allocationsave/', 'sellcard.fornt.cardManage.cardAllocation.allocationSave',name='allocationSave'),
    ################################################# 卡管理 end ###############################################

    ################################################# 卡管理 start ##############################################
    url(r'^fornt/cardsale/orderInfo/$','sellcard.fornt.cardSale.card.info',name='cardsSaleOrderInfo'),
    url(r'^fornt/cardsale/orderInfo/print', 'sellcard.fornt.cardSale.card.reprint', name='cardsSaleOrderReprint'),
    url(r'^fornt/cardsale/orderInfo/explain', 'sellcard.fornt.cardSale.card.print_explain', name='cardsSaleOrderExplain'),
    ################################################# 卡管理 end   ##############################################

    ################################################# 代金券管理 start ################################################
    # 发行代金券
    # 列表
    url(r'^fornt/voucher/issue/$', 'sellcard.fornt.voucherManage.issue.index', name="voucherIssueList"),
    # 创建
    url(r'^fornt/voucher/issue/create/$',
        'sellcard.fornt.voucherManage.issue.create', name="voucherIssueCreate"),
    # 打印
    url(r'^fornt/voucher/issue/printed/$',
        'sellcard.fornt.voucherManage.issue.printed', name="voucherIssuePrint"),

    ################################################# 代金券管理 end ###################################################

    ###########################################  返点折扣授权码 start ##############################################
    #生成
    url(r'^fornt/discode/create/$', 'sellcard.fornt.disCode.create.index',name="disCodeCreate"),
    #分配
    url(r'^fornt/discode/assign/$', 'sellcard.fornt.disCode.assign.index',name="disCodeAssign"),
    #折扣修改授权码校验
    url(r'^fornt/discodecheck/', 'sellcard.common.Method.disCodeCheck',name='disCodeCheck'),
    ###########################################  返点折扣授权码 end  ##############################################

    #卡校验
    url(r'^fornt/cardcheck/$', 'sellcard.common.Method.cardCheck',name='cardcheck'),
    url(r'^fornt/cardcheck2/', 'sellcard.common.Method.cardCheck_Mssql', name='cardcheck_mssql'),
    url(r'^fornt/cardcheck3/', 'sellcard.common.Method.cardCheck_Change', name='cardcheck_change'),
    #兑换码校验
    url(r'^fornt/changcodecheck/', 'sellcard.common.Method.changeCodeCheck',name='changeCodeCheck'),
    #更新赊销状态
    url(r'^fornt/nopay/update', 'sellcard.common.Method.upNoPayStatus',name='upNoPayStatus'),
    #赊销管理
    url(r'^fornt/nopay/$', 'sellcard.fornt.cardSale.nopay.index',name='nopay'),
]