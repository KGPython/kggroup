__author__ = 'qixu'
from django.conf.urls import url
urlpatterns = [
    #购物券销售汇总（财务用）
    url(r'^payment/$', 'sellcard.report.voucher.payment.index', name="voucherPayment"),
    #购物券库存盘点
    #列表
    url(r'^stock/$', 'sellcard.report.voucher.stock.index', name="voucherStock"),
    # 使用明细
    url(r'^stock/detail/$', 'sellcard.report.voucher.stock.detail', name="voucherStockDetail"),
    #购物券核销情况
    # 列表
    url(r'^used/$', 'sellcard.report.voucher.used.index', name="voucherUsed"),
    # 批次明细
    url(r'^used/detail/$', 'sellcard.report.voucher.used.detail', name="voucherUsedDetail"),
    # 详细日期明细
    url(r'^used/detail/date/$', 'sellcard.report.voucher.used.detailDate', name="voucherUsedDetailDate"),
]