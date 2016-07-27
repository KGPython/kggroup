#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
from sellcard.models import CardInventory, OrderChangeCard, OrderChangeCardInfo
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from django.db import transaction

def index(request):
    rates = request.session.get('s_rates')
    return render(request,'cardChange.html',locals())

@csrf_exempt
@transaction.atomic

def save(request):
    operator = request.session.get('s_uid','')
    shopId = request.session.get('s_shopid','')
    roleid= request.session.get("s_roleid",'')

    res = {}
    actionType = request.POST.get('actionType','')

    #入卡列表
    cardListIn = request.POST.get('cardListIn','')
    cardListIn = json.loads(cardListIn)
    #入卡合计
    totalNumIn = request.POST.get('totalNumIn',0)
    totalValIn = request.POST.get('totalValIn',0.00)
    #入卡余额
    balanceIn = request.POST.get('balanceIn',0.00)

    #出卡列表
    cardListOut = request.POST.get('cardListOut','')
    cardListOut = json.loads(cardListOut)
    #出卡合计
    totalNumOut = request.POST.get('totalNumOut',0)
    totalValOut = request.POST.get('totalValOut',0.00)
    #出卡余额
    balanceOut = request.POST.get('balanceOut',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = mtu.setOrderSn()
            created_time=datetime.datetime.today()
            # 入卡插入订单详情
            for cardIn in cardListIn:
                orderInfo = OrderChangeCardInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = cardIn['cardId']
                orderInfo.card_attr = '1'
                orderInfo.card_value = cardIn['cardValue']
                orderInfo.card_balance = float(cardIn['balanceIn'])
                orderInfo.create_time = created_time
                # OrderChangeCard.card_action = '1'
                # OrderChangeCard.card_attr = '3'
                orderInfo.save()
            for cardOut in cardListOut:
                order = OrderChangeCard()
                order.order_id = order_sn
                order.card_id = cardOut['cardId']
                order.card_balance = float(cardOut['cardValOut'])
                order.card_action = '0'
                order.card_attr = '3'
                order.save()

            cardListTotal = cardListIn+cardListOut
            cardIdList = []
            for card in cardListTotal:
                cardIdList.append(card['cardId'])

            mtu.updateCard(cardIdList,'2')
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
            order.discount_rate = discountRate/100

            order.order_sn = order_sn
            order.order_status = 1
            order.save()


            res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0
    return HttpResponse(json.dumps(res))
