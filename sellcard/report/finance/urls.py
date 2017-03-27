from django.conf.urls import url
urlpatterns = [
    #财务报表-库存盘点
    #url(r'^stockCheck/$', 'sellcard.report.finance.stockCheck.index', name="financeStockCheck"),
    #财务报表-借卡统计表
    url(r'^borrowCard/$', 'sellcard.report.finance.borrowCard.index', name="financeBorrowCard"),
]