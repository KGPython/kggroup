from django.conf.urls import url
urlpatterns = [
    #库存盘点--卡类型
    url(r'^report/stock/$', 'sellcard.report.stock.index',name="stock"),
    url(r'^report/stock/cardtype/$', 'sellcard.report.stock.cardType',name="stockGroupByCardType"),
    url(r'^report/stock/cardinfo/$', 'sellcard.report.stock.cardInfo',name="stockGroupByCardNo"),

    #集团销售汇总--按门店分类汇总
    url(r'^report/kgsale/shop/$', 'sellcard.report.saleGroupByShop.index',name="saleGroupByShop"),
    url(r'^report/kgsale/shop/d/$', 'sellcard.report.saleGroupByShop.detail', name="saleGroupByShopDet"),

    #集团销售汇总--按支付分类汇总
    url(r'^report/kgsale/payment/$', 'sellcard.report.saleGroupByPay.index',name="saleGroupByPay"),

    #门店销售汇总--按卡面值分类汇总
    url(r'^report/shopsale/cardtype/$','sellcard.report.saleGroupByCardType.index',name='saleGroupByCardType'),

    #门店销售明细查询
    url(r'^report/shopsale/order/$', 'sellcard.report.saleGroupByOrder.index', name="saleGroupByOrder"),
    #订单明细
    url(r'^report/shopsale/order/info/$', 'sellcard.common.Method.orderDetail',name='orderDetail'),

    #領卡单据盘点
    url('^report/cardSent/order/$','sellcard.report.cardSentGroupByOrder.index',name='sentCardGroupByOrder'),
    url('^report/cardSent/order/info/$','sellcard.report.cardSentGroupByOrder.info',name='cardSentOrderInfo'),

]