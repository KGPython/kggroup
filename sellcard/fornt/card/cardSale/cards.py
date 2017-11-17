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

    return render(request, 'card/sale/cardsSale.html', locals())

def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    listTotal = []
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    for obj in cards:
        sql = " SELECT card_no, card_value, card_blance, card_status,is_store" \
              " FROM card_inventory" \
              " WHERE (card_no >= {start} AND card_no <= {end})" \
              " ORDER BY card_no" \
            .format(start=obj['start'], end=obj['end'])
        cur.execute(sql)
        qs_card = cur.fetchall()
        listTotal.extend(qs_card)

    cardNoList = []
    listTotalNew = []
    for item in listTotal:
        if(item['card_no'] in cardNoList):
            pass
        else:
            cardNoList.append(item['card_no'])
            item['card_blance']=float(item['card_blance'])
            listTotalNew.append(item)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(listTotalNew))