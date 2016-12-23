from django.conf.urls import url

urlpatterns = [


    ################################################# 代金券管理 start ################################################
    # 发行代金券
    # 列表
    url(r'^voucher/issue/$', 'sellcard.fornt.voucherManage.issue.index', name="voucherIssueList"),
    # 创建
    url(r'^voucher/issue/create/$',
        'sellcard.fornt.voucherManage.issue.create', name="voucherIssueCreate"),
    # 打印
    url(r'^voucher/issue/printed/$',
        'sellcard.fornt.voucherManage.issue.printed', name="voucherIssuePrint"),
    # 核销代金券
    # 主页
    url(r'^voucher/balance/$', 'sellcard.fornt.voucherManage.balance.index', name="voucherBalance"),

    ################################################# 代金券管理 end ###################################################

]