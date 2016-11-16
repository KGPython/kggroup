#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json,datetime

from sellcard import views as base
from sellcard.common import Method as mth
from sellcard.models import Allocation,AllocationInfo,CardInventory,ActionLog

# 门店间卡调拨
@csrf_exempt
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    shopCode = request.session.get('s_shopcode','')
    roleid = request.session.get('s_roleid','')
    return render(request,'cardAllocation.html',locals())


@csrf_exempt
@transaction.atomic
def allocationSave(request):

    cardStr = request.POST.get('list','')
    cards = json.loads(cardStr)
    shopIn = request.POST.get('shopIn','')
    shopOut = request.POST.get('shopOut','')
    totalVal = request.POST.get('totalVal','')
    totalNum = request.POST.get('totalNum','')

    res={}
    try:
        orderSn = mth.setOrderSn(Allocation)
        with transaction.atomic():
            allocate = Allocation()
            allocate.order_sn = orderSn
            allocate.shopin_code = shopIn
            allocate.shopout_code = shopOut
            allocate.total_num = int(totalNum)
            allocate.total_value = float(totalVal)
            allocate.add_time = datetime.datetime.now()
            allocate.save()
            for card in cards:
                info = AllocationInfo()
                info.order_sn = orderSn
                info.card_type = float(card['cardType'])
                info.card_nums = card['subTotal']
                info.cardno_start = card['start'].strip()
                info.cardno_end = card['end'].strip()
                info.save()

                CardInventory.objects.filter(card_no__gte=card['start'],card_no__lte=card['end']).update(shop_code=shopIn)

        res['msg']='0'
        ActionLog.objects.create(action='门店卡调拨',u_name=request.session.get('s_uname'),cards_out=cardStr+',shopIn:'+shopIn+',shopOut:'+shopOut,add_time=datetime.datetime.now())

    except Exception as e:
        print(e)
        res['msg']='1'
        ActionLog.objects.create(action='门店卡调拨',u_name=request.session.get('s_uname'),cards_out=cardStr+',shopIn:'+shopIn+',shopOut:'+shopOut,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))
