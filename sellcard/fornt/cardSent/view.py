#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard import views as base
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,json

from sellcard.common import Method as mth
from sellcard.models import CardReceive,ReceiveInfo,CardInventory,MyError

@csrf_exempt
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    return render(request,'cardSent.html',locals())

@csrf_exempt
@transaction.atomic
def sentOrderSave(request):
    orderSn = mth.setOrderSn(CardReceive)

    operator = request.session.get('s_uid','')
    shopId = request.session.get('s_shopid','')

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
                obj = ReceiveInfo()
                obj.rec_id = orderSn
                obj.card_id_start = card['start']
                obj.card_id_end = card['end']
                obj.card_nums = card['subTotal']
                obj.card_value = int(card['cardType'])
                obj.save()
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
                        item.card_value = int(card['cardType'])
                        item.card_action = '1'
                        item.card_status = '1'
                        item.shop_code = shop
                        item.card_blance='0.00'
                        item.card_addtime=datetime.datetime.now()
                        item.save()
        res['msg']='0'
    except MyError as e1:
        print('My exception occurred, value:', e1.value)
        res['msg']='2'
        res['cardId']=e1.value
    except Exception as e:
        print(e)
        res['msg']='1'

    return HttpResponse(json.dumps(res))
