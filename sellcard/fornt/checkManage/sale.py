#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count
import datetime

from sellcard.models import Orders,OrderUpCard
from sellcard.common import Method as mth
@csrf_exempt
def index(request):
    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')
        endTime = datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1)
        saleList = Orders.objects\
                .values('shop_code')\
                .filter(add_time__gte=start,add_time__lte=endTime,action_type__in='1,2,5')\
                .annotate(sale=Sum('paid_amount'),disc=Sum('disc_amount'))\
                .order_by('shop_code')

        fillList = OrderUpCard.objects\
                .values('shop_code')\
                .filter(add_time__gte=start,add_time__lte=endTime)\
                .annotate(diff_value=Sum('diff_price'))\
                .order_by('shop_code')

        saleTotal = 0.00
        discTotal = 0.00
        diffTotal =0.00
        totalInSum = 0.00
        for i in range(0,len(saleList)):
            saleTotal += float(saleList[i]['sale'])
            discTotal +=float(saleList[i]['disc'])
            for j in range(0,len(fillList)):
                if saleList[i]['shop_code'] == fillList[j]['shop_code']:
                    saleList[i]['diff_value'] = float(fillList[j]['diff_value'])
                else:
                    saleList[i]['diff_value'] = 0.00
                saleList[i]['totalIn'] = float(saleList[i]['diff_value'])+float(saleList[i]['sale'])
                diffTotal += saleList[i]['diff_value']
                totalInSum += saleList[i]['totalIn']

    return render(request,'shopSaleCheck.html',locals())

def info(request):
    shop = mth.getReqVal(request,'shop','')
    start = mth.getReqVal(request,'start','')
    end = mth.getReqVal(request,'end','')
    pass