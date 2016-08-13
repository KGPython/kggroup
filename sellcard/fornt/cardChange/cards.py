#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from sellcard.models import CardInventory
from sellcard.common import Method as mth


@csrf_exempt
def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')

    return render(request, 'cardsChange.html',locals())

@csrf_exempt
def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    listTotal = []
    conn = mth.getMssqlConn()
    cur = conn.cursor()
    for obj in cards:
        sql = "select cardno,new_amount,sheetid,mode,detail,memo " \
              "from guest where cardno>='{cardStart}' and cardno<='{cardEnd}'"\
              .format(cardStart=obj['start'],cardEnd=obj['end'])
        cur.execute(sql)
        list = cur.fetchall()
        listTotal.extend(list)
    print(listTotal)

    cardNoList = []
    listTotalNew = []
    for item in listTotal:
        if(item['cardno'] in cardNoList):
            pass
        else:
            cardNoList.append(item['cardno'])
            item['detail']=float(item['detail'])
            item['new_amount']=float(item['new_amount'])
            listTotalNew.append(item)
    return HttpResponse(json.dumps(listTotalNew))