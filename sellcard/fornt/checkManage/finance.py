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
    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')

        cardList = CardInventory.objects\
                .values('shop_code')\
                .filter(charge_time__gte=start,charge_time__lte=end,card_status='1',card_action='1')\
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
    start = request.GET.get('start','')
    end = request.GET.get('end','')
    cardList = CardInventory.objects.values('card_value')\
            .filter(shop_code=shopCode,charge_time__gte=start,charge_time__lte=end,card_status='1',card_action='1')\
            .annotate(num=Count('card_no'),balance=Sum('card_blance'))\
            .order_by('card_value')
    totalBalance = 0.00
    totalNum = 0
    for row in cardList:
        totalBalance += float(row['balance'])
        totalNum +=row['num']
    return render(request,'financeCardTypel.html',locals())


@csrf_exempt
def cardInfo(request):
    shopCode = mth.getReqVal(request,'shopcode','')
    start = mth.getReqVal(request,'start','')
    end = mth.getReqVal(request,'end','')
    cardType = mth.getReqVal(request,'cardtype','')
    page = mth.getReqVal(request,'page',1)

    cardList = CardInventory.objects.values('card_no','card_value','card_blance','card_status','charge_time','sheetid')\
            .filter(card_value=cardType,shop_code=shopCode,charge_time__gte=start,charge_time__lte=end,card_status='1',card_action='1')\
            .order_by('card_no')

    totalBalance = 0.00
    totalNum = 0
    for row in cardList:
        totalBalance += float(row['card_blance'])
        totalNum +=1

    paginator = Paginator(cardList,3)
    try:
        cardList = paginator.page(page)
    except Exception as e:
        print(e)

    return render(request,'financeCardInfo.html',locals())
