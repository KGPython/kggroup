from django.conf.urls import url

urlpatterns = [
    # 库存盘点
    url(r'^stock/$', 'sellcard.report.card.stock.index', name="stock"),
    url(r'^stock/cardtype/$', 'sellcard.report.card.stock.cardType', name="stockGroupByCardType"),
    url(r'^stock/cardinfo/$', 'sellcard.report.card.stock.cardInfo', name="stockGroupByCardNo"),

    # 集团销售汇总--按门店分类汇总
    url(r'^kgsale/shop/$', 'sellcard.report.card.saleGroupByShop.index', name="saleGroupByShop"),
    url(r'^kgsale/shop/d/$', 'sellcard.report.card.saleGroupByShop.detail', name="saleGroupByShopDet"),
    url(r'^kgsale/shop/date/$', 'sellcard.report.card.saleGroupByShop.date_detail', name="saleGroupByShopDateDetail"),

    # 赊销
    url(r'^nopay/order$', 'sellcard.report.card.noPay.order', name="report_card_noPay_order"),
    url(r'^nopay/month$', 'sellcard.report.card.noPay.month', name="report_card_noPay_month"),

    # 集团销售汇总--按支付分类汇总
    url(r'^kgsale/payment/$', 'sellcard.report.card.saleGroupByPay.index', name="saleGroupByPay"),

    # 门店销售汇总--按卡面值分类汇总
    url(r'^shopsale/cardtype/$', 'sellcard.report.card.saleGroupByCardType.index', name='saleGroupByCardType'),

    # 门店销售明细查询
    url(r'^shopsale/order/$', 'sellcard.report.card.saleGroupByOrder.index', name="saleGroupByOrder"),
    url(r'^shopsale/order/info/$', 'sellcard.report.card.saleGroupByOrder.orderDetail', name='orderDetail'),

    url(r'^order/adjust/create$', 'sellcard.report.card.orderAdjust.create', name='orderAdjustCreate'),
    url(r'^order/adjust/$', 'sellcard.report.card.orderAdjust.index', name='orderAdjust'),

    # 領卡单据盘点
    url('^cardSent/order/$', 'sellcard.report.card.cardSentGroupByOrder.index', name='sentCardGroupByOrder'),
    url('^cardSent/order/info/$', 'sellcard.report.card.cardSentGroupByOrder.info', name='cardSentOrderInfo'),

    # 门店费用报销（目前只含有移动积分支付订单）
    url(r'reimbursement/$', 'sellcard.report.card.reimbursement.index', name='reimbursement')

]
