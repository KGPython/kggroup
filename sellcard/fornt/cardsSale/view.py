#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sellcard.models import CardInventory
@csrf_exempt
def index(request):
    operator = request.session.get('s_uid','')
    shopId = request.session.get('s_shopid','')
    roleid= request.session.get("s_roleid",'')
    if request.method == 'POST':
        cardStart = request.POST.get('cardStart','')
        cardEnd = request.POST.get('cardEnd','')
        cardList = CardInventory.objects.values('card_no','card_value','card_status').filter(card_no__gte=cardStart,card_no__lte=cardEnd).order_by('card_no')
        cardTotalVal = 0
        cardTotalNum = 0
        for card in cardList:
            if card['card_status'] == '1':
                cardTotalVal += card['card_value']
                cardTotalNum += 1
    return render(request,'cardsSale.html',locals())