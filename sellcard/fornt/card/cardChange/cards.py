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

    return render(request, 'card/change/cardsChange.html', locals())

def query(request):
    cardsStr = request.POST.get('cards','')
    cards = json.loads(cardsStr)
    cardType = request.POST.get('type','')

    if cardType == 'in':
        listTotalNew = getCardsIn(cards)
    else:
        listTotalNew = getCardsOut(cards)
    return HttpResponse(json.dumps(listTotalNew))

def getCardsIn(cards):
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

    cur.close()
    conn.close()

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
    return listTotalNew

def getCardsOut(cards):
    listTotal = []
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    for obj in cards:
        sql = " SELECT card_no, card_value, card_blance, card_status,is_store"\
              " FROM card_inventory"\
              " WHERE (card_no >= {start} AND card_no <= {end})"\
            .format(start=obj['start'],end=obj['end'])
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
            item['card_value']=item['card_value']
            listTotalNew.append(item)

    cur.close()
    conn.close()
    return listTotalNew