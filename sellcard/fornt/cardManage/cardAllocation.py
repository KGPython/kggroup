#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json,datetime

from sellcard import views as base
from sellcard.common import Method as mth
from sellcard.models import Allocation,AllocationInfo


@csrf_exempt
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    return render(request,'cardAllocation.html',locals())


@csrf_exempt
@transaction.atomic
def sentOrderSave(request):

    cardStr = request.POST.get('list','')
    cards = json.loads(cardStr)
    shopIn = request.POST.get('shopIn','')
    shopOut = request.POST.get('shopOut','')

    res={}
    try:
        orderSn = mth.setOrderSn(Allocation)
        with transaction.atomic():
            allocate = Allocation()
            allocate.order_sn = orderSn
            allocate.shopin_code = shopIn
            allocate.shopout_code = shopOut
            allocate.add_time = datetime.datetime.now()
            allocate.save()
            for card in cards:
                info = AllocationInfo()
                info.order_sn = orderSn

                info.save()

    except Exception as e:
        print(e)
        res['msg']='1'

    return HttpResponse(json.dumps(res))
