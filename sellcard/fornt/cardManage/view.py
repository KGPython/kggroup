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
                    model = CardInventory()
                    # model.card_no = card['CardNO']
                    # model.card_blance = card['detail']
                    # model.card_value = card['detail']
                    # model.card_status = '1'
                    # model.card_action = '1'
                    # model.card_addtime = datetime.datetime.now()
                    # model.save()
                res['msg']='2'
            except Exception as e:
                print(e)
                res['msg']='3'

    return render(request,'cardInStore.html',locals())