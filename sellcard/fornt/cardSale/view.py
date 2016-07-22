#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo,CardInventory
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from django.db import transaction


def index(request):
    return render(request,'cardSale.html',locals())

@csrf_exempt
@transaction.atomic
def saveOrder(request):
    operator = request.session.get('s_uid','')
    shopId = request.session.get('s_shopid','')
    roleid= request.session.get("s_roleid",'')

    res = {}
    actionType = request.POST.get('actionType','')
    #售卡列表
    cardStr = request.POST.get('cardStr','')
    cardList = json.loads(cardStr)
    #赠卡列表
    YcardStr = request.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    #支付方式
    payStr = request.POST.get('payStr','')
    payList = json.loads(payStr)
    #合计信息
    totalNum = request.POST.get('totalNum',0)
    totalVal = request.POST.get('totalVal',0.00)
    YtotalNum = request.POST.get('YtotalNum',0)
    YtotalVal = request.POST.get('YtotalVal',0.00)
    Ybalance = request.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
    order_sn = ''
    try:
        for card in cardList:
            orderInfo = OrderInfo()
            orderInfo.order_id = order_sn
            orderInfo.card_id = card['cardId']
            orderInfo.card_balance = float(card['cardVal'])
            orderInfo.card_action = '0'
            orderInfo.is_give = '0'
            orderInfo.save()
        for Ycard in YcardList:
            YorderInfo = OrderInfo()
            YorderInfo.order_id = order_sn
            YorderInfo.card_id = Ycard['cardId']
            YorderInfo.card_balance = float(Ycard['cardVal'])
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
        order = Orders()
        order.buyer_name = buyerName
        order.buyer_tel = buyerPhone
        order.buyer_company = buyerCompany
        order.total_amount = ''
        order.paid_amount = totalVal
        order.disc_amount = YtotalVal
        order.diff_price = Ybalance
        order.shop_id = shopId
        order.user_id = operator
        order.action_type = actionType
        order.add_time = datetime.datetime.now()
        order_sn = mtu.setOrderSn()
        order.order_sn = order_sn
        order.order_status = 1
        order.save()
        cardListTotal = cardList+YcardList
        cardIdList = []
        for card in cardListTotal:
            cardIdList.append(card['cardId'])
        CardInventory.objects.filter(card_no__in=cardIdList).update(card_status='2',card_action='0')
        res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0
    else:
        pass
        # transaction.commit()
    return HttpResponse(json.dumps(res))