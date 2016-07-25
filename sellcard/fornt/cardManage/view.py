__author__ = 'admin'
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime

from sellcard.common import Method as m
from sellcard.models import CardInventory

@csrf_exempt
@transaction.atomic
def cardInStore(request):
    if request.method=='POST':
        res={}
        orderSn = request.POST.get('orderSn','K001201206060001')
        list = CardInventory.objects.values('order_sn').filter(order_sn=orderSn)
        if(len(list)>0):
            res['msg']='1'
        else:
            sql="SELECT CardNO,detail FROM guest WHERE SheetID ='"+orderSn+"'"
            conn = m.getMssqlConn()
            cur = conn.cursor()
            cur.execute(sql)
            cardList = cur.fetchall()
            conn.close()
            try:
                for card in cardList:
                    model = CardInventory().objects.filter(card_no=card['CardNO'])\
                            .update(card_blance =card['detail'],card_status='1',card_action='1',charge_time=datetime.datetime.now())
                res['msg']='2'
            except Exception as e:
                print(e)
                res['msg']='3'

    return render(request,'cardInStore.html',locals())