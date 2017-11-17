#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
import json,datetime

from sellcard import views as base
from sellcard.common import Method as mth
from sellcard.models import Allocation,AllocationInfo,ActionLog
from sellcard.common.model import MyError

# 门店间卡调拨
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    shopCode = request.session.get('s_shopcode','')
    roleid = request.session.get('s_roleid','')
    return render(request, 'card/manage/cardAllocation.html', locals())


@transaction.atomic
def allocationSave(request):

    cardStr = request.POST.get('list','')
    cards = json.loads(cardStr)
    shopIn = request.POST.get('shopIn','')
    shopOut = request.POST.get('shopOut','')
    totalVal = request.POST.get('totalVal','')
    totalNum = request.POST.get('totalNum','')

    res={}
    try:
        orderSn = mth.setOrderSn(Allocation)
        with transaction.atomic():
            allocate = Allocation()
            allocate.order_sn = orderSn
            allocate.shopin_code = shopIn
            allocate.shopout_code = shopOut
            allocate.total_num = int(totalNum)
            allocate.total_value = float(totalVal)
            allocate.add_time = datetime.datetime.now()
            allocate.save()
            for card in cards:
                info = AllocationInfo()
                info.order_sn = orderSn
                info.card_type = float(card['cardType'])
                info.card_nums = card['subTotal']
                info.cardno_start = card['start'].strip()
                info.cardno_end = card['end'].strip()
                info.save()
                conn = mth.getMysqlConn()
                sql = "update card_inventory set shop_code='{shop}' WHERE card_no BETWEEN {start} AND {end}"\
                    .format(shop=shopIn,start=int(card['start'].strip()),end=int(card['end'].strip()))
                cur = conn.cursor()
                updateNum = cur.execute(sql)
                conn.commit()

                subNum = int(card['end'])-int(card['start'])+1
                if subNum != updateNum :
                    raise MyError(card['start'].strip()+'-'+card['end'].strip()+'状态更新失败')

        res['status']='1'
        ActionLog.objects.create(action='门店卡调拨',u_name=request.session.get('s_uname'),cards_out=cardStr+',shopIn:'+shopIn+',shopOut:'+shopOut,add_time=datetime.datetime.now())

    except Exception as e:
        print(e)
        res['status']='0'
        ActionLog.objects.create(action='门店卡调拨',u_name=request.session.get('s_uname'),cards_out=cardStr+',shopIn:'+shopIn+',shopOut:'+shopOut,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))
