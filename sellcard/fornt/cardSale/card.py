#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo,CardInventory,ExchangeCode
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from django.db import transaction


def index(request):
    rates = request.session.get('s_rates')
    return render(request,'cardSale.html',locals())

@csrf_exempt
@transaction.atomic
def saveOrder(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')

    res = {}
    actionType = request.POST.get('actionType','')
    #售卡列表
    cardStr = request.POST.get('cardStr','')
    cardList = json.loads(cardStr)
    #赠卡列表
    YcardStr = request.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    Ycash = request.POST.get('Ycash','')
    #支付方式
    payStr = request.POST.get('payStr','')
    payList = json.loads(payStr)
    hjsStr = request.POST.get('hjsStr','')
    #黄金手卡号列表
    hjsList=[]
    if len(hjsStr)>0:
        hjsStr = hjsStr[0:len(hjsStr)-1]
        hjsList = hjsStr.split(',')

    #合计信息
    totalNum = request.POST.get('totalNum',0)
    totalVal = request.POST.get('totalVal',0.00)

    discountRate = request.POST.get('discount',0.00)
    YtotalNum = request.POST.get('YtotalNum',0)
    YtotalVal = request.POST.get('YtotalVal',0.00)
    Ybalance = request.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = mtu.setOrderSn()
            for card in cardList:
                orderInfo = OrderInfo()
                orderInfo.order_id = order_sn
                orderInfo.card_id = card['cardId']
                orderInfo.card_balance = float(card['cardVal'])
                orderInfo.card_action = '0'
                orderInfo.card_attr = '1'
                orderInfo.save()
            for Ycard in YcardList:
                YorderInfo = OrderInfo()
                YorderInfo.order_id = order_sn
                YorderInfo.card_id = Ycard['cardId']
                YorderInfo.card_balance = float(Ycard['cardVal'])
                YorderInfo.card_action = '0'
                YorderInfo.card_attr = '2'
                YorderInfo.save()
            for pay in payList:
                orderPay = OrderPaymentInfo()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                if pay['payId']=='4':
                    orderPay.is_pay='0'
                else:
                    orderPay.is_pay='1'
                if pay['payId']=='9':
                    mtu.upChangeCode(hjsList,shopcode)

                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                orderPay.save()

            cardListTotal = cardList+YcardList
            cardIdList = []
            for card in cardListTotal:
                cardIdList.append(card['cardId'])

            mtu.updateCard(cardIdList,'1')
            CardInventory.objects.filter(card_no__in=cardIdList).update(card_status='2',card_action='0')

            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
            order.total_amount = float(totalVal)+float(YtotalVal)
            order.paid_amount = totalVal
            order.disc_amount = YtotalVal
            order.diff_price = Ybalance
            order.shop_code = shopcode
            order.user_id = operator
            order.action_type = actionType
            order.add_time = datetime.datetime.now()
            order.discount_rate = float(discountRate)/100
            order.order_sn = order_sn
            order.y_cash = Ycash
            order.save()


            res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0
    return HttpResponse(json.dumps(res))