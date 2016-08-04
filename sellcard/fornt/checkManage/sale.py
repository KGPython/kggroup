#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count
import datetime
from sellcard.models import Orders
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

        saleTotal = 0.00
        discTotal = 0.00
        for row in saleList:
            saleTotal += float(row['sale'])
            discTotal +=float(row['disc'])

    return render(request,'saleCheck.html',locals())