#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime

from sellcard.common import Method as m
from sellcard.models import Orders,CardInventory
from sellcard import views as base

@csrf_exempt
@transaction.atomic
def cardInStore(request):
    if request.method=='POST':
        res={}
        sheetid = request.POST.get('orderSn','')
        list = CardInventory.objects.values('order_sn').filter(sheetid=sheetid)
        if(len(list)>0):
            res['msg']='1'
        else:
            sql="SELECT CardNO,detail FROM guest WHERE SheetID ='"+sheetid+"'"
            conn = m.getMssqlConn()
            cur = conn.cursor()
            cur.execute(sql)
            cardList = cur.fetchall()
            conn.close()
            try:
                for card in cardList:
                    model = CardInventory.objects.filter(card_no=card['CardNO'])\
                            .update(card_blance =card['detail'],charge_time=datetime.datetime.now(),sheetid=sheetid)
                res['msg']='2'
            except Exception as e:
                print(e)
                res['msg']='3'

    return render(request,'cardInStore.html',locals())

