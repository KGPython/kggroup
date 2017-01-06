from django.conf.urls import url
urlpatterns = [
    #代金券财务用售卖统计
    url(r'^voucher/payment/$', 'sellcard.report.voucher.payment.index', name="voucherPayment"),
    #代金券库存盘点
    url(r'^voucher/stock/$', 'sellcard.report.voucher.stock.index', name="voucherStock"),
    #代金券核销情况
    url(r'^voucher/used/$', 'sellcard.report.voucher.used.index', name="voucherUsed"),
]