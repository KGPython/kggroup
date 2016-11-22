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
        inSubTotal = 0.00
        dataList = []
        shops = base.findShop()

        for i in range(0,len(shops)):
            item = {}
            item['shop_code'] = shops[i]['shop_code']
            for sale in saleList:
                if sale['shop_code']==item['shop_code']:
                    #横向各门店售卡汇总赋值
                    item['sale'] = float(sale['sale'])

                    # 横向累加各门店入账合计并赋值
                    if 'inSub' in item:
                        item['inSub'] += float(sale['sale'])
                    else:
                        item['inSub'] = float(sale['sale'])

                    # 横向累加各门店售卡优惠合计并赋值
                    if 'disc' in item:
                        item['disc'] += float(sale['disc'])
                    else:
                        item['disc'] = float(sale['disc'])

            for fill in fillList:
                if item['shop_code'] == fill['shop_code']:
                    item['fill'] = float(fill['fill'])

                    if 'inSub' in item:
                        item['inSub'] += float(fill['fill'])
                    else:
                        item['inSub'] = float(fill['fill'])
            for change in changeList:
                if item['shop_code'] == change['shop_code']:
                    item['change'] = float(change['change'])

                    if 'inSub' in item:
                        item['inSub'] += float(change['change'])
                    else:
                        item['inSub'] = float(change['change'])

                    if 'disc' in item:
                        item['disc'] += float(change['disc'])
                    else:
                        item['disc'] = float(change['disc'])

            if 'sale' in item:
                saleTotal += float(item['sale'])
            if 'change' in item:
                changeTotal += float(item['change'])
            if 'fill' in item:
                fillTotal += float(item['fill'])
            if 'disc' in item:
                discTotal += float(item['disc'])
            if 'inSub' in item:
                inSubTotal += float(item['inSub'])

            dataList.append(item)

        # print(dataList)
                # saleList[i]['totalIn'] = float(saleList[i]['diff_value'])+float(saleList[i]['sale'])


    return render(request,'shopSaleCheck.html',locals())

def info(request):
    shop = mth.getReqVal(request,'shop','')
    start = mth.getReqVal(request,'start','')
    end = mth.getReqVal(request,'end','')
    pass