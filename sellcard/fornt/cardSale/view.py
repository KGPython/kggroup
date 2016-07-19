#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime

def index(requset):
    return render(requset,'cardSale.html',locals())

@csrf_exempt
def saveOrder(requset):
    operator = requset.session.get('user',1)
    shopId = requset.session.get('group',10)
    res = {}
    #售卡列表
    cardStr = requset.POST.get('cardStr','')
    cardList = json.loads(cardStr)
    #赠卡列表
    YcardStr = requset.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    #支付方式
    payStr = requset.POST.get('payStr','')
    payList = json.loads(payStr)
    #合计信息
    totalNum = requset.POST.get('totalNum',0)
    totalVal = requset.POST.get('totalVal',0.00)
    YtotalNum = requset.POST.get('YtotalNum',0)
    YtotalVal = requset.POST.get('YtotalVal',0.00)
    Ybalance = requset.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = requset.POST.get('buyerName','')
    buyerPhone = requset.POST.get('buyerPhone','')
    buyerCompany = requset.POST.get('buyerCompany','')
    try:
        order = Orders()
        order.buyer_name = buyerName
        order.buyer_tel = buyerPhone
        order.buyer_company = buyerCompany
        order.total_amount = totalVal+YtotalVal
        order.paid_amount = totalVal
        order.disc_amount = YtotalVal
        order.shop_id = shopId
        order.user_id = operator
        order.action_type = 1
        order.add_time = datetime.datetime.now()
        order.order_sn='1321321321'
        order.order_status=1
        order.save()
        res["flag"] = 1
    except Exception as e:
        print(e)
        res["flag"] = 0

    return HttpResponse(json.dumps(res))