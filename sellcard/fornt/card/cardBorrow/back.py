#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json,datetime
from sellcard.models import ActionLog,OrderBorrowInfo,CardInventory
from sellcard.common import Method as mth
from django.db import transaction
from sellcard.common.model import MyError

def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    return render(request, 'borrowBack.html', locals())

def query(request):
    shopcode = request.session.get('s_shopcode','')
    cardsStr = request.POST.get('cards','')
    borrowDepartCode = (request.POST.get('borrowDepartCode','')).strip()
    cards = json.loads(cardsStr)
    listTotal = []
    conn = mth.getMssqlConn()
    cur = conn.cursor()
    #判断余额
    for obj in cards:
        sql = "select cardno,new_amount,sheetid,mode,detail,memo " \
              "from guest where cardno>='{cardStart}' and cardno<='{cardEnd}'"\
              .format(cardStart=obj['start'],cardEnd=obj['end'])
        cur.execute(sql)
        list = cur.fetchall()
        listTotal.extend(list)
    cur.close()
    conn.close()

    #去重复
    cardNoList = []
    listTotalNew = []
    for item in listTotal:
        if(item['cardno'] not in cardNoList):
            cardNoList.append(item['cardno'])
            item['detail']=float(item['detail'])
            item['new_amount']=float(item['new_amount'])
            listTotalNew.append(item)
    #判断是否属于借卡
    for cardNo in cardNoList:
        sql2 = "select b.card_no from order_borrow as a,order_borrow_info as b " \
               "where a.shopcode='"+shopcode+"' and a.order_sn=b.order_sn and a.is_paid='0' and a.borrow_depart_code='"+borrowDepartCode+"' and b.card_no='"+cardNo+"'"
        connSql = mth.getMysqlConn()
        curSql = connSql.cursor()
        curSql.execute(sql2)
        record = curSql.fetchone()

        if not record:
            for card in listTotalNew:
                if card['cardno'] == cardNo:
                    card['is_borrow']='0'
        else:
            for card in listTotalNew:
                if card['cardno'] == cardNo:
                    card['is_borrow']='1'
        curSql.close()
        connSql.close()
    return HttpResponse(json.dumps(listTotalNew))


def save(request):
    cardsStr = request.POST.get('cardStr','')
    cardList = json.loads(cardsStr)
    cardnoList = []
    for card in cardList:
        cardnoList.append(card['cardId'])
    now = datetime.datetime.now()
    res = {}

    # 检测session中Token值，判断用户提交动作是否合法
    Token = request.session.get('postToken', default=None)
    # 获取用户表单提交的Token值
    userToken = request.POST.get('postToken','')
    if userToken != Token:
        res["msg"] = 0
        return HttpResponse(json.dumps(res))

    try:
        with transaction.atomic():
            cardsNum = len(cardnoList)
            resCard = CardInventory.objects.filter(card_no__in=cardnoList).update(card_status='1',card_action='1')
            if resCard != cardsNum:
                raise MyError('系统数据库卡状态更新失败')

            resBorrow = OrderBorrowInfo.objects.filter(card_no__in=cardnoList,is_back=None).update(is_back='1',back_time=now)
            if resBorrow != cardsNum:
                raise MyError('退还卡状态更新失败')

            resErp = mth.updateCard(cardnoList, '9')
            if resErp != cardsNum:
                mth.updateCard(cardnoList, '1')
                raise MyError('ERP数据库卡状态更新失败')

            res['msg'] = 1
            ActionLog.objects.create(action='借卡-还卡',u_name=request.session.get('s_uname'),cards_in=cardsStr,add_time=datetime.datetime.now())
            del request.session['postToken']
    except Exception as e:
        res['msg'] = 0
        res["msg_err"] = e
        ActionLog.objects.create(action='借卡-还卡',u_name=request.session.get('s_uname'),cards_in=cardsStr,add_time=datetime.datetime.now(),err_msg=e)
    return HttpResponse(json.dumps(res))