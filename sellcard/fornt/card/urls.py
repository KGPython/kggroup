from django.conf.urls import url

urlpatterns = [
    ################################################# 售卡模块 start ##############################################
    # 单卡售卡
    url(r'^cardsale/$', 'sellcard.fornt.card.cardSale.card.index', name='cardsale'),
    # 单卡和批量售卡的订单保存
    url(r'^cardsale/saveorder', 'sellcard.fornt.card.cardSale.card.saveOrder', name='saveorder'),
    # 批量售卡
    url(r'^cardssale/$', 'sellcard.fornt.card.cardSale.cards.index', name='cardssale'),
    url(r'^cardssale/query', 'sellcard.fornt.card.cardSale.cards.query', name='cardsSaleQuery'),

    # 大宗赠卡
    url(r'^bestowed/$', 'sellcard.fornt.card.cardSale.bestowed.index', name='bestowed'),
    url(r'^bestowed/save', 'sellcard.fornt.card.cardSale.bestowed.saveOrder', name='bestowedSave'),
    ################################################# 售卡模块 end ###############################################

    ################################################# 换卡模块 start #############################################
    url(r'^cardchange/$', 'sellcard.fornt.card.cardChange.card.index', name='cardchange'),
    url(r'^cardchange/save', 'sellcard.fornt.card.cardChange.card.save', name='cardchange_save'),
    url(r'^cardschange/$', 'sellcard.fornt.card.cardChange.cards.index', name='cardsChange'),
    url(r'^cardschange/query', 'sellcard.fornt.card.cardChange.cards.query', name='cardsChangeQuery'),

    url(r'^cardschange2/$', 'sellcard.fornt.card.cardChange.cards2.index', name='cardsChange2'),
    ################################################# 换卡模块 end ###############################################

    ################################################# 补卡模块 start #############################################
    url(r'^cardfill/index/', 'sellcard.fornt.card.cardFill.view.index', name='cardfill_index'),
    url(r'^cardfill/save', 'sellcard.fornt.card.cardFill.view.save', name='cardfill_save'),
    url(r'^cardfill/query/', 'sellcard.fornt.card.cardFill.view.query', name='cardfill_query'),
    url(r'^cardfill/gocard/', 'sellcard.fornt.card.cardFill.view.gotcard', name='cardfill_gotcard'),
    url(r'^cardfill/update/', 'sellcard.fornt.card.cardFill.view.update', name='cardfill_update'),
    url(r'^cardfill/info/', 'sellcard.fornt.card.cardFill.view.info', name='cardfill_info'),
    ################################################# 补卡模块 end ###############################################

    ################################################# 借卡模块 end ###############################################
    # 借卡
    url(r'^borrow/sale/index/', 'sellcard.fornt.card.cardBorrow.sale.index', name='borrowSale'),
    url(r'^borrow/sale/save/', 'sellcard.fornt.card.cardBorrow.sale.save', name='borrowSaleSave'),
    url(r'^borrow/sale/info/', 'sellcard.fornt.card.cardBorrow.sale.info', name='borrowSaleInfo'),

    # 退卡
    url(r'^borrow/back/index/', 'sellcard.fornt.card.cardBorrow.back.index', name='borrowBack'),
    url(r'^borrow/back/query/', 'sellcard.fornt.card.cardBorrow.back.query', name='borrowBackQuery'),
    url(r'^borrow/back/save/', 'sellcard.fornt.card.cardBorrow.back.save', name='borrowBackSave'),
    # 结算
    url(r'^borrow/pay/index/', 'sellcard.fornt.card.cardBorrow.pay.index', name='borrowPay'),
    url(r'^borrow/pay/save/', 'sellcard.fornt.card.cardBorrow.pay.save', name='borrowPaySave'),
    ################################################# 借卡管理 end ###############################################

    ################################################# 卡管理 start ##############################################
    # 领卡
    url(r'^cardSent/$', 'sellcard.fornt.card.cardSent.view.index', name='cardSent'),
    url(r'^cardSent/save', 'sellcard.fornt.card.cardSent.view.sentOrderSave', name='sentOrderSave'),
    # 卡入库
    url(r'^cardmanage/cardinstore/', 'sellcard.fornt.card.cardManage.view.cardInStore', name='cardInStore'),
    # 卡调拨
    url(r'^cardmanage/cardallocation/', 'sellcard.fornt.card.cardManage.cardAllocation.index',
        name='cardAllocation'),
    url(r'^cardmanage/allocationsave/', 'sellcard.fornt.card.cardManage.cardAllocation.allocationSave',
        name='allocationSave'),
    ################################################# 卡管理 end ###############################################

    ################################################# 卡管理 start ##############################################
    # 售卡打印订单
    url(r'^cardsale/orderInfo/$', 'sellcard.fornt.card.cardSale.card.info', name='cardsSaleOrderInfo'),
    url(r'^cardsale/orderInfo/print', 'sellcard.fornt.card.cardSale.card.reprint', name='cardsSaleOrderReprint'),
    url(r'^cardsale/orderInfo/explain', 'sellcard.fornt.card.cardSale.card.print_explain',
        name='cardsSaleOrderExplain'),
    # 更换卡打印订单
    url(r'^cardChange/orderInfo/$', 'sellcard.fornt.card.cardChange.card.info', name='cardChangeOrderInfo'),
    ################################################# 卡管理 end   ##############################################



    ###########################################  返点折扣授权码 start ##############################################
    # 生成
    url(r'^discode/create/$', 'sellcard.fornt.card.disCode.create.index', name="disCodeCreate"),
    # 分配
    url(r'^discode/assign/$', 'sellcard.fornt.card.disCode.assign.index', name="disCodeAssign"),
    # 折扣修改授权码校验
    url(r'^discodecheck/', 'sellcard.common.Method.disCodeCheck', name='disCodeCheck'),
    ###########################################  返点折扣授权码 end  ##############################################


    ###########################################  到账管理 start ##############################################
    # 普通赊销到账
    url(r'^nopay/ordinary/$', 'sellcard.fornt.card.noPay.ordinary.index', name='nopay'),
    url(r'^nopay/ordinary/update/$', 'sellcard.common.Method.upNoPayStatus', name='upNoPayStatus'),

    #移动积分到账
    url(r'^nopay/yd/$', 'sellcard.fornt.card.noPay.yidong.index', name='YDNoPay'),

    ###########################################  到账管理 start ##############################################


    # 卡校验
    url(r'^cardcheck/$', 'sellcard.common.Method.cardCheck', name='cardcheck'),
    url(r'^cardcheck2/', 'sellcard.common.Method.cardCheck_Mssql', name='cardcheck_mssql'),
    url(r'^cardcheck3/', 'sellcard.common.Method.cardCheck_Change', name='cardcheck_change'),
    # 兑换码校验
    url(r'^changcodecheck/', 'sellcard.common.Method.changeCodeCheck', name='changeCodeCheck'),



]