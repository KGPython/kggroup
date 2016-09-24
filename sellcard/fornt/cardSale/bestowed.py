#-*- coding:utf-8 -*-
__author__ = 'admin'

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from sellcard.models import Orders,OrderInfo,CardInventory,ActionLog
import datetime
from sellcard.common import Method as mtu
from django.http import HttpResponse
from sellcard.common.model import MyError
def index(reauest):
    return render(reauest, 'bestowed.html',locals())

@csrf_exempt
@transaction.atomic
def saveOrder(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    res = {}
    #售卡列表
    cardStr = request.POST.get('cardsStr','')
    cardList = json.loads(cardStr)

    #合计信息
    totalNum = request.POST.get('totalNum',0)
    totalVal = request.POST.get('totalVal',0.00)
    remark = request.POST.get('remarks','')
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
                orderInfo.card_attr = '2'
                orderInfo.save()
            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
            order.total_amount = float(totalVal)
            order.paid_amount = 0
            order.disc_amount = float(totalVal)
            order.diff_price = 0
            order.shop_code = shopcode
            order.depart = depart
            order.operator_id = operator
            order.action_type = '5'
            order.add_time = datetime.datetime.now()
            order.order_sn = order_sn
            order.remark = remark
            order.save()

            #更新
            cardIdList = []
            for card in cardList:
                cardIdList.append(card['cardId'])
            cardNum = len(cardIdList)

            resCard = CardInventory.objects.filter(card_no__in=cardIdList).update(card_status=2,card_action='0')
            if resCard!= cardNum:
                raise MyError('系统数据库卡状态更新失败')

            resErp = mtu.updateCard(cardIdList,'1')
            if resErp!= cardNum:
                mtu.updateCard(cardIdList,'9')
                raise MyError('ERP数据库卡状态更新失败')

            res["msg"] = 1
            res["urlRedirect"] = '/kg/sellcard/cardsale/orderInfo/?orderSn='+order_sn
            ActionLog.objects.create(action='实物团购返点',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now())

    except Exception as e:
        res["msg_err"] = e.value
        res["msg"] = 0
        ActionLog.objects.create(action='实物团购返点',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))