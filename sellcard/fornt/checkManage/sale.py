#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count
import datetime

from sellcard.models import Orders,OrderUpCard,OrderChangeCard
from sellcard.common import Method as mth
from sellcard import views as base
@csrf_exempt
def index(request):
    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')
        endTime = datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1)
        saleList = Orders.objects\
                .values('shop_code')\
                .filter(add_time__gte=start,add_time__lte=endTime,action_type__in='1,2,3,5')\
                .annotate(sale=Sum('paid_amount'),disc=Sum('disc_amount'))\
                .order_by('shop_code')

        fillList = OrderUpCard.objects\
                .values('shop_code')\
                .filter(add_time__gte=start,add_time__lte=endTime)\
                .annotate(fill=Sum('diff_price'))\
                .order_by('shop_code')

        changeList = OrderChangeCard.objects\
                .values('shop_code')\
                .filter(add_time__gte=start,add_time__lte=endTime)\
                .annotate(change=Sum('total_out_price')-Sum('total_in_price')+Sum('disc_pay'),disc=Sum('disc'))\
                .order_by('shop_code')

        saleTotal = 0.00
        changeTotal = 0.00
        fillTotal = 0.00
        discTotal = 0.00

        dataList = []

        for i in range(0,len(saleList)):
            item = {}
            #纵向累加所有门店售卡合计
            saleTotal += float(saleList[i]['sale'])
            #横向各门店售卡汇总赋值
            item['sale'] = float(saleList[i]['sale'])

            # 纵向累加所有门店优惠合计
            discTotal +=float(saleList[i]['disc'])
            # 横向累加各门店售卡优惠合计并赋值
            if saleList[i]['disc']==0:
                item['disc'] = float(saleList[i]['disc'])
            else:
                item['disc'] += float(saleList[i]['disc'])

            for fill in fillList:
                if saleList[i]['shop_code'] == fill['shop_code']:
                    item['fill'] = float(fill['fill'])
                    fillTotal += fill['fill']
            for change in changeList:
                if saleList[i]['shop_code'] == change['shop_code']:
                    item['change'] = float(change['change'])
                    changeTotal += change['change']
            dataList.append(item)
                # saleList[i]['totalIn'] = float(saleList[i]['diff_value'])+float(saleList[i]['sale'])


    return render(request,'shopSaleCheck.html',locals())

def info(request):
    shop = mth.getReqVal(request,'shop','')
    start = mth.getReqVal(request,'start','')
    end = mth.getReqVal(request,'end','')
    pass