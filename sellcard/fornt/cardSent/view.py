#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard import views as base
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,json

from sellcard.common import Method as mth
from sellcard.models import CardReceive,ReceiveInfo,CardInventory,ActionLog
from sellcard.common.model import MyError

@csrf_exempt
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    return render(request,'cardSent.html',locals())

@csrf_exempt
@transaction.atomic
def sentOrderSave(request):
    orderSn = 'SE'+mth.setOrderSn(CardReceive)

    cardStr = request.POST.get('list','')
    cards = json.loads(cardStr)
    shop = request.POST.get('shop','')
    person = request.POST.get('person','')

    res={}
    try:
        with transaction.atomic():
            receive = CardReceive()
            receive.rec_sn = orderSn
            receive.shop_code = shop
            receive.rec_name = person
            receive.add_time = datetime.datetime.now()
            receive.save()
            for card in cards:
                if card['cardType']=='无面值':
                    card['cardType'] = ''

                obj = ReceiveInfo()
                obj.rec_id = orderSn
                obj.card_id_start = card['start']
                obj.card_id_end = card['end']
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
                    item.card_no = prefix+str(i)
                    num = CardInventory.objects.filter(card_no=prefix+str(i)).count()
                    if(num>0):
                        raise MyError(prefix+str(i))
                    else:
                        item.card_value = card['cardType']
                        item.card_action = '1'
                        item.card_status = '1'
                        item.shop_code = shop
                        item.card_blance='0.00'
                        item.card_addtime=datetime.datetime.now()
                        item.save()
        res['msg']='0'
        ActionLog.objects.create(action='信息部发卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now())

    except MyError as e1:
        print('My exception occurred, value:', e1.value)
        res['msg']='2'
        res['cardId']=e1.value
        ActionLog.objects.create(action='信息部发卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e1.value)

    except Exception as e:
        print(e)
        res['msg']='1'
        ActionLog.objects.create(action='信息部发卡',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))
