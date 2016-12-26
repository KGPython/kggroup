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


    #验证码发放
    url(r'^voucher/verifier/sent/$', 'sellcard.fornt.voucher.verifier.sent.index', name="verifierSent"),
    url(r'^voucher/verifier/sent/save/$', 'sellcard.fornt.voucher.verifier.sent.save', name="verifierSentSave"),


    # 生成验证码
    url(r'^voucher/verifier/create/$', 'sellcard.fornt.voucher.verifier.create.index', name="voucherVerifierCreate"),
    # 检验券真伪
    url(r'^voucher/verifier/verifier/$', 'sellcard.fornt.voucher.verifier.verifier.index', name="voucherVerifier"),

]