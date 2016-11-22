#-*- coding:utf-8 -*-
from django.shortcuts import render

from sellcard import views as base
from django.views.decorators.csrf import csrf_exempt

import datetime,json

from sellcard.common import Method as mth
from sellcard.models import ReceiveInfo

@csrf_exempt
def index(request):
    shops = base.findShop()
    if request.method == 'POST':
        shop = request.POST.get('shop','')
        if shop:
            whereShop = 'shop_code = "{shop}"'.format(shop=shop)
        else:
            whereShop ='1=1'
        start = request.POST.get('start')
        end = request.POST.get('end')
        nextDay = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)

        sqlOrder = 'select a.rec_sn,a.shop_code,a.add_time,a.rec_name,SUM(b.card_nums) as card_nums from card_receive as a, receive_info as b ' \
                   'where a.rec_sn=b.rec_id and add_time >= "{start}" and add_time<="{nextDay}" and {whereShop} group by b.rec_id order by a.shop_code,a.add_time'\
                   .format(start=start,nextDay=nextDay,whereShop=whereShop)
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        cur.execute(sqlOrder)
        orders = cur.fetchall()

    return render(request, 'report/sentCardGroupByOrder.html', locals())

def info(request):
    order_sn = request.GET.get('order_sn')
    recInfoList = ReceiveInfo.objects.values('card_value','card_nums','card_id_start','card_id_end')\
                    .filter(rec_id=order_sn).order_by('card_value')

    totalNum = 0
    totalVal = 0.00
    for recInfo in recInfoList:
        totalNum += int(recInfo['card_nums'])

    return render(request, 'report/cardSentOrderInfo.html', locals())