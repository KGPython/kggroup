#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.shortcuts import render
from django.db.models import Sum,Count
from django.core.paginator import Paginator #分页查询
import datetime

from sellcard.models import CardInventory,Shops
from sellcard.common import Method as mth

def index(request):
    shopCode = mth.getReqVal(request,'shopcode','')
    cardType = mth.getReqVal(request,'cardtype','')
    page = mth.getReqVal(request,'page',1)

    cardList = CardInventory.objects.values('card_no','card_value','card_blance','card_status','charge_time','sheetid')\
            .filter(card_blance=cardType,shop_code=shopCode,card_status='1',card_action='1',card_blance__gt='0')\
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

    return render(request, 'report/stockGroupByCardNo.html', locals())
