#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json

from sellcard.models import CardInventory
from sellcard.common import Method as mth


def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    return render(request, 'cardsChange.html', locals())

def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    listTotal = []
    conn = mth.getMssqlConn()
    cur = conn.cursor()
    for obj in cards:
        if obj['end']:
            sql = "select cardno,new_amount,sheetid,mode,detail,memo " \
                  "from guest where cardno>='{cardStart}' and cardno<='{cardEnd}'"\
                  .format(cardStart=obj['start'],cardEnd=obj['end'])
        else:
            sql = "select cardno,new_amount,sheetid,mode,detail,memo " \
                  "from guest where cardno='{cardStart}'"\
                  .format(cardStart=obj['start'],cardEnd=obj['end'])
        cur.execute(sql)
        list = cur.fetchall()
        listTotal.extend(list)

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