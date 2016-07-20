#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo,CardInventory
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from django.db import transaction


def index(requset):
    return render(requset,'cardSale.html',locals())

@csrf_exempt
# @transaction.non_atomic_requests
@transaction.atomic
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
    order_sn = ''
    try:
        order = Orders()
        order.buyer_name = buyerName
        order.buyer_tel = buyerPhone
        order.buyer_company = buyerCompany
        order.total_amount = float(totalVal)+float(YtotalVal)
        order.paid_amount = totalVal
        order.disc_amount = YtotalVal
        order.diff_price = Ybalance
        order.shop_id = shopId
        order.user_id = operator
        order.action_type = 1
        order.add_time = datetime.datetime.now()
        order_sn = mtu.setOrderSn()
        order.order_sn = order_sn
        order.order_status = 1
        order.save()

        for card in cardList:
            orderInfo = OrderInfo()
            orderInfo.order_id = order_sn
            orderInfo.card_id = card['cardId']
            orderInfo.card_balance = card['cardVal']
            orderInfo.card_action = '0'
            orderInfo.is_give = '0'
            orderInfo.save()
        for Ycard in YcardList:
            YorderInfo = OrderInfo()
            YorderInfo.order_id = order_sn
            YorderInfo.card_id = Ycard['cardId']
            YorderInfo.card_balance = Ycard['cardVal']
            YorderInfo.card_action = '0'
            YorderInfo.is_give = '1'
            YorderInfo.save()
        for pay in payList:
            orderPay = OrderPaymentInfo()
            orderPay.order_id = order_sn
            orderPay.pay_id = pay['payId']
            orderPay.pay_value = pay['payVal']
            orderPay.remarks = pay['payRmarks']
            orderPay.save()

        cardListTotal = cardList+YcardList
        cardIdList = []
        for card in cardListTotal:
            cardIdList.append(card['cardId'])
        CardInventory.objects.filter(card_no__in=cardIdList).update(card_status=2)
        res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0
    return HttpResponse(json.dumps(res))