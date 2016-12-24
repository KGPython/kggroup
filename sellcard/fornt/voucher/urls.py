from django.conf.urls import url

urlpatterns = [

    # 发行代金券
    # 列表
    url(r'^voucher/issue/$', 'sellcard.fornt.voucher.issue.index', name="voucherIssueList"),
    # 创建
    url(r'^voucher/issue/create/$',
        'sellcard.fornt.voucher.issue.create', name="voucherIssueCreate"),
    # 打印
    url(r'^voucher/issue/printed/$',
        'sellcard.fornt.voucher.issue.printed', name="voucherIssuePrint"),
    # 核销代金券
    # 主页
    url(r'^voucher/balance/$', 'sellcard.fornt.voucher.balance.index', name="voucherBalance"),
    # 生成验证码
    # 主页
    url(r'^voucher/verifier/create/$', 'sellcard.fornt.voucher.verifier.create.index', name="voucherVerifierCreate"),
    # 检验券真伪
    # 主页
    url(r'^voucher/verifier/verifier/$', 'sellcard.fornt.voucher.verifier.verifier.index', name="voucherVerifier"),

]