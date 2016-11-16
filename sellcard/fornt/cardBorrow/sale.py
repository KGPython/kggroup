#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum,Count
import json,datetime

from sellcard.common import Method as mth
from sellcard.models import OrderBorrow,OrderBorrowInfo,CardInventory,ActionLog
from sellcard.common.model import MyError
@csrf_exempt
def index(request):
    return render(request, 'borrowSale.html',locals())

@csrf_exempt
def save(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')

    res = {}
    #售卡列表
    cardStr = request.POST.get('cardStr','')
    cardList = json.loads(cardStr)

    #合计信息
    totalNum = request.POST.get('totalNum',0)
    totalVal = request.POST.get('totalVal',0.00)

    #借卡人信息
    borrowDepart = (request.POST.get('borrowDepart','')).strip()
    borrowName = (request.POST.get('borrowName','')).strip()
    borrowDepartCode = (request.POST.get('borrowDepartCode','')).strip()
    borrowPhone = (request.POST.get('borrowPhone','')).strip()

    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = 'B'+mth.setOrderSn(OrderBorrow)
            for card in cardList:
                orderInfo = OrderBorrowInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = card['cardId']
                orderInfo.card_type = card['cardVal']
                orderInfo.card_balance = card['cardVal']
                orderInfo.save()

            order = OrderBorrow()
            order.borrow_name = borrowName
            order.borrow_depart = borrowDepart
            order.borrow_depart_code = borrowDepartCode
            order.borrow_phone= borrowPhone
            order.shopcode = shopcode
            order.operator = operator
            order.order_val = float(totalVal)
            order.order_num = totalNum
            order.add_time = datetime.datetime.now()
            order.is_paid = '0'
            order.order_sn = order_sn
            order.save()

            #更新卡状态
            cardListTotal = cardList
            cardIdList = []
            for card in cardListTotal:
                cardIdList.append(card['cardId'])
            cardNum = len(cardIdList)

            resCard = CardInventory.objects.filter(card_no__in=cardIdList).update(card_status='2',card_action='0')
            if resCard != cardNum:
                raise MyError('系统数据库卡状态更新失败！')
            resErp = mth.updateCard(cardIdList,'1')
            if resErp != cardNum:
                mth.updateCard(cardIdList,'9')
                raise MyError('ERP数据库卡状态更新失败！')
            res["msg"] = 1
            res["urlRedirect"] = '/kg/sellcard/borrow/sale/info/?orderSn='+order_sn
            ActionLog.objects.create(action='借卡-售卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now())
    except Exception as e:
        print(e)
        res["msg"] = 0
        res["msg_err"] = e.value
        ActionLog.objects.create(action='借卡-售卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e.value)

    return HttpResponse(json.dumps(res))


def info(request):
    orderSn = request.GET.get('orderSn','')
    today = datetime.date.today()

    order = OrderBorrow\
            .objects\
            .values('shopcode','order_val','order_num','operator','borrow_depart','borrow_depart_code','borrow_name','borrow_phone','add_time')\
            .filter(order_sn=orderSn)
    infoList = OrderBorrowInfo\
                .objects.values('card_balance')\
                .filter(order_sn=orderSn)\
                .annotate(subVal=Sum('card_balance'),subNum=Count('card_no'))

    totalNum = 0
    for info in infoList:
        totalNum += int(info['subNum'])
    return render(request,'borrowOrderInfo.html',locals())

