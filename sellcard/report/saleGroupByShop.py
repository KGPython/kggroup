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

    saleDiscGroupByShop = 'select shop_code,SUM(disc_amount) as disc,SUM(y_cash) as disc_cash, SUM(disc_amount-y_cash) as disc_card ' \
                          'from orders ' \
                          'where add_time>="{start}" and add_time<="{end}" ' \
                          'group by shop_code ' \
                          .format(start=start, end=endTime)
    cur.execute(saleDiscGroupByShop)
    saleDiscList = cur.fetchall()

    salePayGroupByShop = 'select ord.shop_code,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                'from orders as ord , order_payment_info as info ' \
                'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.order_sn = info.order_id ' \
                'group by ord.shop_code,info.pay_id' \
                .format(start=start, end=endTime)
    cur.execute(salePayGroupByShop)
    salePayList = cur.fetchall()


    fillList = OrderUpCard.objects\
            .values('shop_code')\
            .filter(add_time__gte=start,add_time__lte=endTime)\
            .annotate(fill=Sum('diff_price'))\
            .order_by('shop_code')

    changeDiscGroupByShop = 'select shop_code,SUM(disc) as disc,SUM(disc_cash) as disc_cash,(SUM(disc-disc_cash)) as disc_card ' \
                  'from order_change_card ' \
                  'where add_time>="{start}" and add_time<="{end}" ' \
                  'group by shop_code ' \
                  .format(start=start, end=endTime)
    cur.execute(changeDiscGroupByShop)
    changeDiscList = cur.fetchall()
    changePayGroupByShop = 'select ord.shop_code ,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                           'from order_change_card as ord , order_change_card_payment as info ' \
                           'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.order_sn = info.order_id ' \
                           'group by ord.shop_code,info.pay_id' \
                           .format(start=start, end=endTime)
    cur.execute(changePayGroupByShop)
    changePayList = cur.fetchall()


    totalDict  = {'discTotal':0,'discCashTotal':0,'discCardTotal':0,'inSubTotal':0,'total_1':0,'total_2':0,'total_3':0,
                  'total_4':0,'total_5':0,'total_6':0,'total_7':0,'total_8':0,'total_9':0,}
    dataList = []
    shops = base.findShop()

    for i in range(0,len(shops)):
        item = {'shop_code':'','disc':0,'disc_cash':0,'disc_card':0,'inSub':0,'pay_1':0,'pay_2':0,'pay_3':0,
                'pay_4':0,'pay_5':0,'pay_6':0,'pay_7':0,'pay_8':0,'pay_9':0,}
        item['shop_code'] = shops[i]['shop_code']
        for sale in salePayList:
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

        for saleDisc in saleDiscList:
            if saleDisc['shop_code'] == item['shop_code']:
                if not saleDisc['disc']:
                    saleDisc['disc'] = 0
                item['disc'] += float(saleDisc['disc'])
                item['disc_cash'] += float(saleDisc['disc_cash'])
                item['disc_card'] += float(saleDisc['disc_card'])

        for fill in fillList:
            if item['shop_code'] == fill['shop_code']:
                item['pay_1'] += float(fill['fill'])
                item['inSub'] = float(fill['fill'])

        for change in changePayList:
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
        for changeDisc in changeDiscList:
            if changeDisc['shop_code'] == item['shop_code']:
                if not changeDisc['disc']:
                    changeDisc['disc'] = 0
                item['disc'] += float(changeDisc['disc'])
                item['disc_cash'] += float(changeDisc['disc_cash'])
                item['disc_card'] += float(changeDisc['disc_card'])

        totalDict['discTotal'] += item['disc']
        totalDict['discCashTotal'] += item['disc_cash']
        totalDict['discCardTotal'] += item['disc_card']
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
        print(dataList)
    return render(request, 'report/saleGroupByShop.html', locals())





