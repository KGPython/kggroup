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
    shopCode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    res = {}
    actionType = request.POST.get('actionType','')

    #入卡列表
    cardListIn = request.POST.get('cardListIn','')
    cardListIn = json.loads(cardListIn)
    #入卡合计
    totalNumIn = request.POST.get('totalNumIn',0)
    totalValIn = request.POST.get('totalValIn',0.00)

    #出卡列表
    cardListOut = request.POST.get('cardListOut','')
    cardListOut = json.loads(cardListOut)
    #出卡合计
    totalNumOut = request.POST.get('totalNumOut',0)
    totalValOut = request.POST.get('totalValOut',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')

    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = mtu.setOrderSn(OrderChangeCard)
            created_time=datetime.datetime.today()
            # 入卡插入订单详情
            for cardIn in cardListIn:
                orderInfo = OrderChangeCardInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = cardIn['cardId']
                orderInfo.card_attr = '1'
                orderInfo.card_value = cardIn['cardVal']
                orderInfo.card_balance = cardIn['cardVal']
                orderInfo.add_time = created_time
                orderInfo.save()
            for cardOut in cardListOut:
                orderInfo = OrderChangeCardInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = cardOut['cardId']
                orderInfo.card_attr = '0'
                orderInfo.card_value = cardOut['cardVal']
                orderInfo.card_balance = cardOut['cardVal']
                orderInfo.add_time = created_time
                orderInfo.save()

            cardIdInList = []
            for card in cardListIn:
                cardIdInList.append(card['cardId'])
            cardIdOutList = []
            for card in cardListOut:
                cardIdOutList.append(card['cardId'])

            mtu.updateCard(cardIdOutList,'1')
            mtu.updateCard(cardIdInList,'2')
            CardInventory.objects.filter(card_no__in=cardIdInList).update(card_status='1',card_action='1')
            CardInventory.objects.filter(card_no__in=cardIdOutList).update(card_status='2',card_action='0')
            order = OrderChangeCard()
            order.order_sn = order_sn
            order.operator_id = operator
            order.depart = depart
            order.shop_code = shopCode
            order.user_name = buyerName
            order.user_phone = buyerPhone
            order.total_in_amont = totalNumIn
            order.total_in_price = totalValIn
            order.total_out_amount = totalNumOut
            order.total_out_price = totalValOut
            order.add_time = created_time
            order.save()


            res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0
    return HttpResponse(json.dumps(res))
