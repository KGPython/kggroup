#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo,CardInventory,ActionLog
from django.http import HttpResponse
import json,datetime
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count

from sellcard.common import Method as mtu

def index(request):
    operator = request.session.get('s_uid','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')
    shopcode = request.session.get('s_shopcode','')
    return render(request,'cardSale.html',locals())


@csrf_exempt
@transaction.atomic
def saveOrder(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')


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
    disCode = request.POST.get('disCode','')
    discountVal = request.POST.get('discountVal','')
    YtotalNum = request.POST.get('YtotalNum',0)

    Ybalance = request.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = 'S'+mtu.setOrderSn()
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
            mtu.updateDisCode(disCode,shopcode,order_sn)
            CardInventory.objects.filter(card_no__in=cardIdList).update(card_status='2',card_action='0')

            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
            order.total_amount = float(totalVal)+float(discountVal)
            order.paid_amount = float(totalVal)+float(Ybalance)#实付款合计=售卡合计+优惠补差
            order.disc_amount = float(discountVal)#优惠合计
            order.diff_price = Ybalance
            order.shop_code = shopcode
            order.depart = depart
            order.operator_id = operator
            order.action_type = actionType
            order.add_time = datetime.datetime.now()
            order.discount_rate = float(discountRate)/100
            order.order_sn = order_sn
            order.y_cash = Ycash
            order.save()

            res["msg"] = 1
            res["urlRedirect"] = '/kg/sellcard/cardsale/orderInfo/?orderSn='+order_sn
            path = request.path
            ActionLog.objects.create(url=path,u_name=request.session.get('s_uname'),cards_out=cardStr+','+YcardStr,add_time=datetime.datetime.now())
    except Exception as e:
        print(e)
        res["msg"] = 0
        ActionLog.objects.create(url=path,u_name=request.session.get('s_uname'),cards_out=cardStr+','+YcardStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))


def info(request):
    orderSn = request.GET.get('orderSn','')
    today = datetime.date.today()

    order = Orders.objects\
            .values('shop_code','operator_id','paid_amount','disc_amount','diff_price','y_cash','buyer_name','add_time')\
            .filter(order_sn=orderSn)
    infoList = OrderInfo.objects.values('card_balance','card_attr').filter(order_id=orderSn).annotate(subVal=Sum('card_balance'),subNum=Count('card_id'))

    totalNum = 0
    for info in infoList:
        totalNum += int(info['subNum'])
    return render(request,'orderInfo.html',locals())