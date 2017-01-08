__author__ = 'qixu'
from django.conf.urls import url
urlpatterns = [
    #代金券销售汇总（财务用）
    url(r'^payment/$', 'sellcard.report.voucher.payment.index', name="voucherPayment"),
    #代金券库存盘点
    #列表
    url(r'^stock/$', 'sellcard.report.voucher.stock.index', name="voucherStock"),
    # 使用明细
    url(r'^stock/detail/$', 'sellcard.report.voucher.stock.detail', name="voucherStockDetail"),
    #代金券核销情况
    # 列表
    url(r'^used/$', 'sellcard.report.voucher.used.index', name="voucherUsed"),
    # 批次明细
    url(r'^used/detail/$', 'sellcard.report.voucher.used.detail', name="voucherUsedDetail"),
]