#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard import views as base
from django.db import transaction
import datetime,json

from sellcard.common import Method as mth
from sellcard.models import CardReceive,ReceiveInfo,CardInventory,ActionLog
from sellcard.common.model import MyError

def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    return render(request, 'card/sent/cardSent.html', locals())

@transaction.atomic
def sentOrderSave(request):
    orderSn = 'G'+mth.setOrderSn(CardReceive)
    res = {}
    # 检测session中Token值，判断用户提交动作是否合法
    Token = request.session.get('postToken', default=None)
    # 获取用户表单提交的Token值
    userToken = request.POST.get('postToken', '')
    if userToken != Token:
        raise MyError('表单重复提交，CTRL+F5刷新页面后，重试！')

    cardStr = request.POST.get('list','')
    cards = json.loads(cardStr)
    shop = request.POST.get('shop','')
    person = request.POST.get('person','')
    saleType = request.POST.get('saleType','')


    try:
        with transaction.atomic():
            receive = CardReceive()
            receive.rec_sn = orderSn
            receive.shop_code = shop
            receive.rec_name = person
            receive.add_time = datetime.datetime.now()
            receive.save()

            cardList = []
            for card in cards:
                if card['cardType']=='无面值':
                    card['cardType'] = ''
                obj = ReceiveInfo()
                obj.rec_id = orderSn
                obj.card_id_start = card['start'].strip()
                obj.card_id_end = card['end'].strip()
                obj.card_nums = card['subTotal']
                obj.card_value = card['cardType']
                obj.save()

                #CardInventory写入卡信息
                for i in range(int(card['start']),int(card['end'])+1):
                    diff = len(card['start'])-len(str(int(card['start'])))
                    prefix = ''
                    for j in range(diff):
                       prefix +='0'
                    item = CardInventory()
                    item.order_sn = orderSn
                    item.is_store = saleType
                    item.card_no = prefix+str(i)
                    item.card_value = card['cardType']
                    item.card_action = '1'
                    item.card_status = '1'
                    item.shop_code = shop
                    item.card_blance='0.00'
                    item.card_addtime=datetime.datetime.now()
                    cardList.append(item)
            CardInventory.objects.bulk_create(cardList)
        res['status']='1'
        ActionLog.objects.create(action='信息部发卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now())
        del request.session['postToken']
    except Exception as e:
        print(e)
        if hasattr(e,'value'):
            res['msg'] = e.value
        res['status']='0'
        ActionLog.objects.create(action='信息部发卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e)
    return HttpResponse(json.dumps(res))

