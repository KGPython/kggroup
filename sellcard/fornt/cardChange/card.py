#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
from sellcard.models import CardInventory, OrderChangeCard, OrderChangeCardInfo,ActionLog
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from sellcard.common.model import MyError
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

    #入卡列表
    cardListInStr = request.POST.get('cardListIn','')
    cardListIn = json.loads(cardListInStr)
    #入卡合计
    totalNumIn = request.POST.get('totalNumIn',0)
    totalValIn = request.POST.get('totalValIn',0.00)

    #出卡列表
    cardListOutStr = request.POST.get('cardListOut','')
    cardListOut = json.loads(cardListOutStr)
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
            # 保存
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

            #更新
            cardIdInList = []
            for card in cardListIn:
                cardIdInList.append(card['cardId'])
            cardIdOutList = []
            for card in cardListOut:
                cardIdOutList.append(card['cardId'])
            cardsOutNum = len(cardIdOutList)
            cardsInNum = len(cardIdInList)

            resCardIn = CardInventory.objects.filter(card_no__in=cardIdInList).update(card_status='1',card_action='1')
            resCardOut = CardInventory.objects.filter(card_no__in=cardIdOutList).update(card_status='2',card_action='0')
            if resCardIn != cardsInNum or resCardOut != cardsOutNum:
                raise MyError('系统数据库卡状态更新失败')

            resErpOut = mtu.updateCard(cardIdOutList,'1')
            resErpIn = mtu.updateCard(cardIdInList,'9')
            if resErpIn != cardsInNum or resErpOut != cardsOutNum:
                mtu.updateCard(cardIdOutList,'9')
                mtu.updateCard(cardIdOutList,'1')
                raise MyError('ERP数据库卡状态更新失败')

            res["msg"] = 1
            ActionLog.objects.create(action='换卡-单卡',u_name=request.session.get('s_uname'),cards_in=cardListInStr,cards_out=cardListOutStr,add_time=datetime.datetime.now())
    except Exception as e:
        res["msg"] = 0
        res["msg_err"] = e.value
        ActionLog.objects.create(action='换卡-单卡',u_name=request.session.get('s_uname'),cards_in=cardListInStr,cards_out=cardListOutStr,add_time=datetime.datetime.now(),err_msg=e.value)

    return HttpResponse(json.dumps(res))
