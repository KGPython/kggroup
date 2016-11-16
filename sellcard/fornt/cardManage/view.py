#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,json

from sellcard.common import Method as m
from sellcard.models import ActionLog,CardInventory

# 卡入库
@csrf_exempt
@transaction.atomic
def cardInStore(request):
    if request.method=='POST':
        shop = request.session.get("s_shopcode",'')

        res={}
        conn = m.getMssqlConn()
        cur = conn.cursor()
        sheetid = (request.POST.get('orderSn','')).strip()
        findSheetCode = "SELECT note FROM batchsalepaytype WHERE SheetID ='"+sheetid+"'"
        cur.execute(findSheetCode)
        shopDict  = cur.fetchone()
        if not shopDict:
            res['msg']='5'
        else:
            if shopDict['note'].strip() != shop:
                res['msg']='4'
            else:
                list = CardInventory.objects.values('order_sn').filter(sheetid=sheetid)
                if(len(list)>0):
                    res['msg']='1'
                else:
                    sql="SELECT CardNO,detail FROM guest WHERE SheetID ='"+sheetid+"'"

                    cur.execute(sql)
                    cardList = cur.fetchall()
                    conn.close()
                    try:
                        for card in cardList:
                            CardInventory.objects.filter(card_no=card['CardNO'])\
                                    .update(card_blance =card['detail'],card_value =card['detail'],charge_time=datetime.datetime.now(),sheetid=sheetid)
                            card['detail'] = float(card['detail'])
                        res['msg']='2'
                        ActionLog.objects.create(action='门店卡入库',u_name=request.session.get('s_uname'),cards_in=json.dumps(cardList),add_time=datetime.datetime.now())

                    except Exception as e:
                        print(e)
                        res['msg']='3'
                        ActionLog.objects.create(action='门店卡入库',u_name=request.session.get('s_uname'),cards_in=json.dumps(cardList),add_time=datetime.datetime.now(),err_msg=e)

    return render(request,'cardInStore.html',locals())
