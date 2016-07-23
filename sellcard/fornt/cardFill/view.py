#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import OrderUpCard,OrderUpCardInfo,CardInventory
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mtu
from django.db import transaction

def index(reauest):

    return render(reauest,'cardFill.html',locals())

def query(reauest):

    return render(reauest,'cardFillQuery.html',locals())

@csrf_exempt
@transaction.atomic
def save(request):
    operator_id = request.session.get('s_uid','')
    shop_id = request.session.get('s_shopid','')

    res = {}
    #入卡列表
    cardInStr = request.POST.get('cardInStr','')
    cardInList = json.loads(cardInStr)
    #入卡合计
    cardInTotalNum = request.POST.get('cardInTotalNum',0)
    cardInTotalVal = request.POST.get('cardInTotalVal',0.00)

    #补卡人信息
    user_name = request.POST.get('user_name','')
    user_phone = request.POST.get('user_phone','')
    action_type = request.POST.get('action_type','')

    try:
        with transaction.atomic():
            order_sn = mtu.setOrderSn()

            order = OrderUpCard()
            order.order_sn=order_sn
            order.action_type=action_type
            order.total_amount=cardInTotalNum
            order.total_price=cardInTotalVal
            order.user_name=user_name
            order.user_phone=user_phone
            order.state=1
            order.shop_id=shop_id
            order.operator_id=operator_id
            order.created_time=datetime.datetime.today()
            order.save()

            #订单明细：入卡,待补的卡即待作废的卡
            cardIdInList = []
            for card in cardInList:
                info = OrderUpCardInfo()
                info.order_sn=order_sn
                info.card_no=card["cardId"]
                info.card_value=card["cardVal"]
                info.card_balance=card["balance"]
                info.card_attr=1
                info.created_time=datetime.datetime.today()
                info.save()

                cardIdInList.append(card['cardId'])

            #冻结旧卡
            CardInventory.objects.filter(card_no__in=cardIdInList).update(card_status=4)

            res["msg"] = 1
    except Exception as e:
        print(e)
        res["msg"] = 0

    return HttpResponse(json.dumps(res))

def update(request):
    pass
    # 激活新卡
    # if orderStatus=="1":
    #     cardIdOutList = []
    #     for card2 in cardOutList:
    #         cardIdOutList.append(card2['cardId'])
    #     CardInventory.objects.filter(card_no__in=cardIdOutList).update(card_status=2)

    # 回写卡库，待完成

