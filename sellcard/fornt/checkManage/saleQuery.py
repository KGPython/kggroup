#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import datetime,time

from sellcard.common import Method as mth
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo,OrderUpCard,OrderUpCardInfo,OrderChangeCard,OrderChangeCardInfo

@csrf_exempt
def index(request):
    today = str(datetime.date.today())
    # now = datetime.datetime.strftime()
    shop = mth.getReqVal(request,'shop','')
    depart = mth.getReqVal(request,'depart','')
    operator = mth.getReqVal(request,'operator','')
    actionType = mth.getReqVal(request,'shop','')
    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    endTime = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(1)

    resList=[]
    if actionType=='1':
        resList = Orders.objects.values('shop_code','user_id').filter().annotate()
    elif actionType=='2':
        pass
    elif actionType=='3':
        pass
    shop = "shop='"+shop+"" if shop else ''
    depart = "depart='"+depart+"" if depart else ''
    operator = "shop='"+operator+"" if operator else ''
    actionType = "shop='"+actionType+"" if actionType else ''

    return  render(request,'saleQuery.html',locals())