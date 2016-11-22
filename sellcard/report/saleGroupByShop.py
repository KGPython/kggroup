#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count
import datetime

from sellcard.models import Orders,OrderUpCard,OrderChangeCard
from sellcard.common import Method as mth
from sellcard import views as base
@csrf_exempt
def index(request):
    if request.method == 'GET':
        start = str(datetime.date.today().replace(day=1))
        end = str(datetime.date.today())
        endTime =str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'POST':
        today = datetime.date.today()
        start = request.POST.get('start',today)
        end = request.POST.get('end',today)
        endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    sqlToSale = 'select ord.shop_code,SUM(ord.disc_amount) as disc ,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                  'from orders as ord , order_payment_info as info ' \
                  'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.order_sn = info.order_id and info.is_pay = "1" ' \
                  'group by ord.shop_code,info.pay_id' \
        .format(start=start, end=endTime)
    cur.execute(sqlToSale)
    saleList = cur.fetchall()


    fillList = OrderUpCard.objects\
            .values('shop_code')\
            .filter(add_time__gte=start,add_time__lte=endTime)\
            .annotate(fill=Sum('diff_price'))\
            .order_by('shop_code')

    sqlToChange = 'select ord.shop_code,SUM(ord.disc) as disc ,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                  'from order_change_card as ord , order_change_card_payment as info ' \
                  'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.order_sn = info.order_id and info.is_pay = "1" ' \
                  'group by ord.shop_code,info.pay_id' \
                  .format(start=start, end=endTime)
    cur.execute(sqlToChange)
    changeList = cur.fetchall()

    totalDict  = {'discTotal':0,'inSubTotal':0,'total_1':0,'total_2':0,'total_3':0,
                  'total_4':0,'total_5':0,'total_6':0,'total_7':0,'total_8':0,'total_9':0,}
    dataList = []
    shops = base.findShop()

    for i in range(0,len(shops)):
        item = {'shop_code':'','disc':0,'inSub':0,'pay_1':0,'pay_2':0,'pay_3':0,
                'pay_4':0,'pay_5':0,'pay_6':0,'pay_7':0,'pay_8':0,'pay_9':0,}
        item['shop_code'] = shops[i]['shop_code']
        for sale in saleList:
            if sale['shop_code']==item['shop_code']:
                #横向各门店售卡汇总赋值
                if sale['pay_id'] == 1:
                    item['pay_1'] += float(sale['pay_value'])
                if sale['pay_id'] == 2:
                    item['pay_2'] += float(sale['pay_value'])
                if sale['pay_id'] == 3:
                    item['pay_3'] += float(sale['pay_value'])
                if sale['pay_id'] == 4:
                    item['pay_4'] += float(sale['pay_value'])
                if sale['pay_id'] == 5:
                    item['pay_5'] += float(sale['pay_value'])
                if sale['pay_id'] == 6:
                    item['pay_6'] += float(sale['pay_value'])
                if sale['pay_id'] == 7:
                    item['pay_7'] += float(sale['pay_value'])
                if sale['pay_id'] == 8:
                    item['pay_8'] += float(sale['pay_value'])
                if sale['pay_id'] == 9:
                    item['pay_9'] += float(sale['pay_value'])

                item['inSub'] += float(sale['pay_value'])
                item['disc'] += float(sale['disc'])

        for fill in fillList:
            if item['shop_code'] == fill['shop_code']:
                item['pay_1'] += float(fill['fill'])
                item['inSub'] = float(fill['fill'])

        for change in changeList:
            if item['shop_code'] == change['shop_code']:
                # 横向各门店售卡汇总赋值
                if sale['pay_id'] == 1:
                    item['pay_1'] += float(change['pay_value'])
                if sale['pay_id'] == 2:
                    item['pay_2'] += float(change['pay_value'])
                if sale['pay_id'] == 3:
                    item['pay_3'] += float(change['pay_value'])
                if sale['pay_id'] == 4:
                    item['pay_4'] += float(change['pay_value'])
                if sale['pay_id'] == 5:
                    item['pay_5'] += float(change['pay_value'])
                if sale['pay_id'] == 6:
                    item['pay_6'] += float(change['pay_value'])
                if sale['pay_id'] == 7:
                    item['pay_7'] += float(change['pay_value'])
                if sale['pay_id'] == 8:
                    item['pay_8'] += float(change['pay_value'])
                if sale['pay_id'] == 9:
                    item['pay_9'] += float(change['pay_value'])

                item['inSub'] = float(change['pay_value'])
                item['disc'] += float(change['disc'])
        totalDict['discTotal'] += item['disc']
        totalDict['inSubTotal'] += item['inSub']
        totalDict['total_1'] += item['pay_1']
        totalDict['total_2'] += item['pay_2']
        totalDict['total_3'] += item['pay_3']
        totalDict['total_4'] += item['pay_4']
        totalDict['total_5'] += item['pay_5']
        totalDict['total_6'] += item['pay_6']
        totalDict['total_7'] += item['pay_7']
        totalDict['total_8'] += item['pay_8']
        totalDict['total_9'] += item['pay_9']

        dataList.append(item)

    return render(request, 'report/saleGroupByShop.html', locals())





