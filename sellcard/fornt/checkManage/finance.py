#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count
from django.core.paginator import Paginator #分页查询
import datetime

from sellcard.models import CardInventory
from sellcard.common import Method as mth


@csrf_exempt
def index(request):
    role_id = request.session.get('s_roleid')
    shop_code = request.session.get('s_shopcode')

    kwargs = {}
    kwargs.setdefault('card_status','1')
    kwargs.setdefault('card_action','1')
    kwargs.setdefault('card_blance__gt','0')
    if role_id=='2':
        kwargs.setdefault('shop_code',shop_code)

    cardList = CardInventory.objects\
            .values('shop_code')\
            .filter(**kwargs)\
            .exclude(shop_code='')\
            .annotate(num=Count('card_no'),balance=Sum('card_blance'))\
            .order_by('shop_code')

    totalBalance = 0.00
    totalNum = 0
    for row in cardList:
        totalBalance += float(row['balance'])
        totalNum +=row['num']
    return render(request,'financeCheck.html',locals())

def cardType(request):
    shopCode = request.GET.get('shopcode','')

    cardList = CardInventory.objects.values('card_blance')\
            .filter(shop_code=shopCode,card_status='1',card_action='1',card_blance__gt='0')\
            .annotate(num=Count('card_no'),balance=Sum('card_blance'))\
            .order_by('card_blance')
    totalBalance = 0.00
    totalNum = 0
    for row in cardList:
        totalBalance += float(row['balance'])
        totalNum +=row['num']
    return render(request,'financeCardTypel.html',locals())


@csrf_exempt
def cardInfo(request):
    shopCode = mth.getReqVal(request,'shopcode','')
    cardType = mth.getReqVal(request,'cardtype','')
    page = mth.getReqVal(request,'page',1)

    cardList = CardInventory.objects.values('card_no','card_value','card_blance','card_status','charge_time','sheetid')\
            .filter(card_value=cardType,shop_code=shopCode,card_status='1',card_action='1',card_blance__gt='0')\
            .order_by('card_no')

    totalBalance = 0.00
    totalNum = 0
    for row in cardList:
        totalBalance += float(row['card_blance'])
        totalNum +=1

    paginator = Paginator(cardList,20)
    try:
        cardList = paginator.page(page)
    except Exception as e:
        print(e)

    return render(request,'financeCardInfo.html',locals())
