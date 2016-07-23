#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sellcard.models import CardInventory
from sellcard.common import Method as mtu

@csrf_exempt
def index(request):
    operator = request.session.get('s_uid','')
    shopId = request.session.get('s_shopid','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')
    if request.method == 'POST':
        cardStart = request.POST.get('cardStart','')
        cardEnd = request.POST.get('cardEnd','')

        conn = mtu.getMysqlConn()
        sql = 'SELECT card_no,card_value,card_status,card_blance FROM card_inventory ' \
              'WHERE card_no >='+cardStart+' and card_no <='+cardEnd+' ORDER BY card_no'
        cur = conn.cursor()
        cur.execute(sql)
        cardList = cur.fetchall()
        conn.close()

        cardTotalVal = 0.00
        cardTotalNum = 0
        for card in cardList:
            if card['card_status'] == '1' and card['card_value']==card['card_blance']:
                cardTotalVal += card['card_value']
                cardTotalNum += 1
        rate=0
        discountVal=0
        for obj in rates:
            if obj['val_min']<=cardTotalVal and obj['val_max']>=cardTotalVal:
                rate = obj['discount_rate']*100
                discountVal = cardTotalVal*rate/100
    return render(request,'cardsSale.html',locals())