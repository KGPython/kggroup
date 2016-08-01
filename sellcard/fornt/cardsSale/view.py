#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from sellcard.models import CardInventory
from sellcard.common import Method as mtu


@csrf_exempt
def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')

    return render(request,'cardsSale.html',locals())

@csrf_exempt
def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    listTotal = []
    for obj in cards:
        list = CardInventory.objects.filter(card_no__gte=obj['start'],card_no__lte=obj['end'])\
            .values('card_no','card_value','card_status','card_blance').order_by('card_no')
        listTotal.extend(list)
    for item in listTotal:
        item['card_value']=float(item['card_value'])
        item['card_blance']=float(item['card_blance'])
    return HttpResponse(json.dumps(listTotal))