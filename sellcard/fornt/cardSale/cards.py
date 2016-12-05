#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json

from sellcard.models import CardInventory
from sellcard.common import Method as mtu


def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    return render(request, 'cardsSale.html',locals())

def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    listTotal = []
    for obj in cards:
        list = CardInventory.objects.filter(card_no__gte=obj['start'],card_no__lte=obj['end'])\
            .values('card_no','card_value','card_status','card_blance').order_by('card_no')
        listTotal.extend(list)

    cardNoList = []
    listTotalNew = []
    for item in listTotal:
        if(item['card_no'] in cardNoList):
            pass
        else:
            cardNoList.append(item['card_no'])
            item['card_blance']=float(item['card_blance'])
            listTotalNew.append(item)
    return HttpResponse(json.dumps(listTotalNew))