__author__ = 'qixu'
from django.conf.urls import url

urlpatterns = [

    # 发行代金券
    # 列表
    url(r'^issue/$', 'sellcard.fornt.voucher.issue.index', name="voucherIssueList"),
    # 创建
    url(r'^issue/create/$',
        'sellcard.fornt.voucher.issue.create', name="voucherIssueCreate"),
    # 打印
    url(r'^issue/printed/$',
        'sellcard.fornt.voucher.issue.printed', name="voucherIssuePrint"),


    # 核销代金券
    # 主页
    url(r'^balance/$', 'sellcard.fornt.voucher.balance.index', name="voucherBalance"),


    # 过期券核销
    # 主页
    url(r'^overdue/$', 'sellcard.fornt.voucher.overdue.index', name="voucherOverdue"),


    #验证码发放
    url(r'^verifier/sent/$', 'sellcard.fornt.voucher.verifier.sent.index', name="verifierSent"),
    url(r'^verifier/sent/save/$', 'sellcard.fornt.voucher.verifier.sent.save', name="verifierSentSave"),


    # 生成验证码
    url(r'^verifier/create/$', 'sellcard.fornt.voucher.verifier.create.index', name="voucherVerifierCreate"),
    # 检验券真伪
    url(r'^verifier/verifier/$', 'sellcard.fornt.voucher.verifier.verifier.index', name="voucherVerifier"),

    # 赊销代金券
    #列表
    url(r'^credit/$', 'sellcard.fornt.voucher.credit.index', name="voucherCredit"),
    #赊销操作Get
    url(r'^credit/create/$', 'sellcard.fornt.voucher.credit.create', name="voucherCreditCreate"),
    #赊销操作Post
    url(r'^credit/create/save/$', 'sellcard.fornt.voucher.credit.createSave', name="voucherCreditCreateSave"),

]