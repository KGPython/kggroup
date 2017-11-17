#-*- coding:utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import OrderUpCard,Payment
from sellcard.common import Method as mth
from sellcard import views as base

def getData(role_id,shop,start,endTime):
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    if role_id == '1' or role_id == '6':
        shops = mth.getCityShops()
        shopsCode = mth.getCityShopsCode()
    elif role_id == '9':
        shops = mth.getCityShops('T')
        shopsCode = mth.getCityShopsCode('T')
    elif role_id == '8':
        shops = mth.getCityShops('C')
        shopsCode = mth.getCityShopsCode('C')
    elif role_id == '10' or role_id == '2' or role_id == '12' or role_id == '11':
        shops = base.findShop(shop)
        shopsCode = [shop]

    shopsCodeStr = "'" + "','".join(shopsCode) + "'"
    # shopsCodeStr = "('C003')"
    # saleDiscGroupByShop = 'SELECT a.shop_code, SUM(CASE WHEN b.card_balance<= a.diff_price THEN a.y_cash+b.card_balance ELSE a.disc_amount END ) AS disc,' \
    #                       'SUM(a.y_cash) AS disc_cash,SUM(case WHEN b.card_balance<= a.diff_price THEN b.card_balance ELSE b.card_balance-a.diff_price END) AS disc_card ' \
    #                       'FROM orders AS a ' \
    #                       'LEFT JOIN (SELECT  order_id,SUM(card_balance) AS card_balance ' \
    #                       'FROM order_info WHERE card_attr="2" GROUP BY order_id,card_attr) AS b ' \
    #                       'ON b.order_id = a.order_sn ' \
    #                       'WHERE a.add_time >= "{start}" AND a.add_time <= "{end}" AND a.shop_code IN ({shopsCodeStr}) group by a.shop_code '\
    #                      .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)

    saleDiscGroupByShop = 'select shop_code,' \
                          'SUM(case when disc_amount>=y_cash then disc_amount else diff_price+disc_amount end) as disc, ' \
                          'SUM(y_cash) as disc_cash, ' \
                          'SUM(case when disc_amount>=y_cash then disc_amount-y_cash else disc_amount+diff_price-y_cash end) as disc_card ' \
                          'from orders ' \
                          'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr}) ' \
                          'group by shop_code ' \
                          .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(saleDiscGroupByShop)
    saleDiscList = cur.fetchall()

    salePayGroupByShop = 'select ord.shop_code,info.pay_id,info.change_time,SUM(info.pay_value) as pay_value ' \
                         'from orders as ord , order_payment_info as info ' \
                         'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.shop_code in ({shopsCodeStr})' \
                         ' and ord.order_sn = info.order_id ' \
                         'group by ord.shop_code,info.pay_id,info.change_time ' \
                        .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(salePayGroupByShop)
    salePayList = cur.fetchall()

    fillList = OrderUpCard.objects \
        .values('shop_code') \
        .filter(add_time__gte=start, add_time__lte=endTime, shop_code__in=shopsCode) \
        .annotate(fill=Sum('diff_price')) \
        .order_by('shop_code')

    # changeDiscGroupByShop = 'SELECT a.shop_code, SUM(CASE WHEN b.card_balance<= a.disc_pay THEN a.disc_cash+b.card_balance ELSE a.disc END) AS disc,' \
    #                         'SUM(a.disc_cash) AS disc_cash,SUM(case WHEN b.card_balance<= a.disc_pay THEN b.card_balance ELSE b.card_balance-a.disc_pay END) AS disc_card ' \
    #                         'FROM order_change_card AS a '\
    #                         'LEFT JOIN (SELECT  order_sn,sum(card_balance) as card_balance ' \
    #                         'FROM order_change_card_info where type="1" group by order_sn,type)'\
    #                         'AS b on b.order_sn = a.order_sn '\
    #                         'WHERE a.add_time >= "{start}" AND a.add_time <= "{end}" AND a.shop_code IN ({shopsCodeStr}) ' \
    #                         'group by a.shop_code ' \
    #                         .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)

    changeDiscGroupByShop = 'select shop_code,SUM(case when disc>=disc_cash then disc else disc_pay+disc end) as disc,' \
                            'SUM(disc_cash) as disc_cash,' \
                            'SUM(case when disc>=disc_cash then disc-disc_cash else disc+disc_pay-disc_cash end) as disc_card ' \
                            'from order_change_card ' \
                            'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr}) ' \
                            'group by shop_code ' \
                            .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(changeDiscGroupByShop)
    changeDiscList = cur.fetchall()
    changePayGroupByShop = 'select ord.shop_code ,info.pay_id,info.change_time,SUM(info.pay_value) as pay_value ' \
                           'from order_change_card as ord , order_change_card_payment as info ' \
                           'where ord.add_time>="{start}" and ord.add_time<="{end}" and shop_code in ({shopsCodeStr}) and ord.order_sn = info.order_id ' \
                           'group by ord.shop_code,info.pay_id,info.change_time' \
                            .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(changePayGroupByShop)
    changePayList = cur.fetchall()

    paymentsRate = Payment.objects.values('id', 'dis_rate').filter(dis_rate__gte=0)
    paymentsRateDict = {item['id']: float(item['dis_rate']) for item in paymentsRate}
    totalDict = {'discTotal': 0,
                 'discCashTotal': 0, 'total_disc_6': 0, 'total_disc_7': 0, 'total_disc_8': 0, 'total_disc_10': 0,
                 'total_disc_11': 0, 'total_disc_qita': 0, 'discCardTotal': 0,
                 'inSubTotal': 0, 'total_1': 0, 'total_2': 0, 'total_3': 0,
                 'total_4': 0, 'total_5': 0, 'total_6': 0, 'total_7': 0, 'total_8': 0, 'total_9': 0, 'total_10': 0,
                 'total_11': 0, }

    dataList = []
    for i in range(0, len(shops)):
        # shopcode = shops[i]['shop_code']
        if shops[i]['shop_code'] != 'ZBTG':
            item = {'shop_code': '',
                    'disc': 0, 'disc_6': 0, 'disc_7': 0, 'disc_8': 0, 'disc_10': 0, 'disc_11': 0, 'disc_cash': 0,
                    'disc_card': 0,
                    'inSub': 0, 'pay_1': 0, 'pay_2': 0, 'pay_3': 0, 'pay_4': 0, 'pay_5': 0, 'pay_6': 0, 'pay_7': 0,
                    'pay_8': 0,
                    'pay_9': 0, 'pay_10': 0, 'pay_11': 0, }
            item['shop_code'] = shops[i]['shop_code']
            for sale in salePayList:
                if sale['shop_code'] == item['shop_code']:
                    # 横向各门店售卡汇总赋值
                    # pay_id = sale['pay_id']
                    if sale['pay_id'] == 1:
                        item['pay_1'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 2:
                        item['pay_2'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 3:
                        item['pay_3'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 4:
                        item['pay_4'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 5:
                        item['pay_5'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 6:
                        item['pay_6'] += float(sale['pay_value'])
                        item['disc_6'] += float(sale['pay_value']) * paymentsRateDict[6]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 7:
                        item['pay_7'] += float(sale['pay_value'])
                        item['disc_7'] += float(sale['pay_value']) * paymentsRateDict[7]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 8:
                        item['pay_8'] += float(sale['pay_value'])
                        item['disc_8'] += float(sale['pay_value']) * paymentsRateDict[8]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 9:
                        item['pay_9'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 10:
                        item['pay_10'] += float(sale['pay_value'])
                        item['disc_10'] += float(sale['pay_value']) * paymentsRateDict[10]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 11:
                        item['pay_11'] += float(sale['pay_value'])
                        item['disc_11'] += float(sale['pay_value']) * paymentsRateDict[11]
                        item['inSub'] += float(sale['pay_value'])

            for saleDisc in saleDiscList:
                if saleDisc['shop_code'] == item['shop_code']:
                    if not saleDisc['disc']:
                        saleDisc['disc'] = 0
                    if not saleDisc['disc_cash']:
                        saleDisc['disc_cash'] = 0
                    if not saleDisc['disc_card']:
                        saleDisc['disc_card'] = 0
                    item['disc'] += float(saleDisc['disc'])
                    item['disc_cash'] += float(saleDisc['disc_cash'])
                    item['disc_card'] += float(saleDisc['disc_card'])

            for fill in fillList:
                if item['shop_code'] == fill['shop_code']:
                    if not fill['fill']:
                        fill['fill'] = 0

                    item['pay_1'] += float(fill['fill'])
                    item['inSub'] += float(fill['fill'])

            for change in changePayList:
                if item['shop_code'] == change['shop_code']:
                    # 横向各门店售卡汇总赋值
                    if change['pay_id'] == 1:
                        item['pay_1'] += float(change['pay_value'])
                    if change['pay_id'] == 2:
                        item['pay_2'] += float(change['pay_value'])
                    if change['pay_id'] == 3:
                        item['pay_3'] += float(change['pay_value'])
                    if change['pay_id'] == 5:
                        item['pay_5'] += float(change['pay_value'])
                    if change['pay_id'] == 6:
                        item['pay_6'] += float(change['pay_value'])
                        item['disc_6'] += float(change['pay_value']) * paymentsRateDict[6]
                    if change['pay_id'] == 7:
                        item['pay_7'] += float(change['pay_value'])
                        item['disc_7'] += float(change['pay_value']) * paymentsRateDict[7]
                    if change['pay_id'] == 8:
                        item['pay_8'] += float(change['pay_value'])
                        item['disc_8'] += float(change['pay_value']) * paymentsRateDict[8]
                    if change['pay_id'] == 9:
                        item['pay_9'] += float(change['pay_value'])
                    if change['pay_id'] == 10:
                        item['pay_10'] += float(change['pay_value'])
                        item['disc_10'] += float(change['pay_value']) * paymentsRateDict[10]
                    if change['pay_id'] == 11:
                        item['pay_11'] += float(change['pay_value'])
                        item['disc_11'] += float(change['pay_value']) * paymentsRateDict[11]

                    item['inSub'] += float(change['pay_value'])

            for changeDisc in changeDiscList:
                if changeDisc['shop_code'] == item['shop_code']:
                    if not changeDisc['disc']:
                        changeDisc['disc'] = 0
                    if not changeDisc['disc_cash']:
                        changeDisc['disc_cash'] = 0
                    if not changeDisc['disc_card']:
                        changeDisc['disc_card'] = 0
                    item['disc'] += float(changeDisc['disc'])
                    item['disc_cash'] += float(changeDisc['disc_cash'])
                    item['disc_card'] += float(changeDisc['disc_card'])

            totalDict['discTotal'] += item['disc']
            totalDict['discCashTotal'] += item['disc_cash']
            totalDict['total_disc_6'] += item['disc_6']
            totalDict['total_disc_7'] += item['disc_7']
            totalDict['total_disc_8'] += item['disc_8']
            totalDict['total_disc_10'] += item['disc_10']
            totalDict['total_disc_11'] += item['disc_11']
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
            totalDict['total_10'] += item['pay_10']
            totalDict['total_11'] += item['pay_11']

            dataList.append(item)
    totalDict['total_disc_qita'] = totalDict['discCashTotal'] - totalDict['total_disc_6'] - totalDict['total_disc_7'] \
                                   - totalDict['total_disc_8'] - totalDict['total_disc_10'] - totalDict['total_disc_11']

    return dataList,totalDict


def index(request):
    shop = request.session.get('s_shopcode','')
    role_id = request.session.get('s_roleid')
    if request.method == 'GET':
        start = str(datetime.date.today().replace(day=1))
        end = str(datetime.date.today())
        endTime =str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'POST':
        today = datetime.date.today()
        start = request.POST.get('start',today)
        end = request.POST.get('end',today)
        endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))

    dataList, totalDict = getData(role_id, shop, start, endTime)
    return render(request, 'report/card/saleGroupByShop/index.html', locals())


def detail(request):
    today = datetime.date.today()
    page = mth.getReqVal(request, 'page', 1)
    shop_code = request.GET.get('shop')
    pay_id = request.GET.get('pay_id')

    shop = request.session.get('s_shopcode', '')
    role_id = request.session.get('s_roleid')
    if role_id == '9':
        shopsCode = mth.getCityShopsCode('T')
        if shop_code not in shopsCode:
            return render(request, '500.html', locals())
    elif role_id == '8':
        shopsCode = mth.getCityShopsCode('C')
        if shop_code not in shopsCode:
            return render(request, '500.html', locals())
    elif role_id == '10' or role_id == '2' or role_id == '12':
        if shop != shop_code:
            return render(request, '500.html', locals())


    start = request.GET.get('start', today)
    end = request.GET.get('end', today)
    endTime = str(datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1))

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    if pay_id == '3':
        sql = " select a.order_sn,a.action_type,b.is_pay,b.pay_value,c.bank_name,c.bank_sn,c.pay_company" \
              " from orders as a inner join order_payment_info as b on a.order_sn = b.order_id left join order_payment_credit as c on a.order_sn = c.order_id"\
              " where a.add_time>='{start}' and a.add_time<='{end}' and a.shop_code ='{shop}' and b.pay_id=3" \
              " order by b.is_pay,a.order_sn"\
              .format(start=start, end=endTime, shop=shop_code)
    else:
        sql = " select a.order_sn,a.action_type,a.buyer_name,a.buyer_tel,a.buyer_company,b.pay_value,b.is_pay" \
              " from orders as a ,order_payment_info as b" \
              " where a.order_sn = b.order_id and a.shop_code = '{shop}' and a.add_time >= '{start}'" \
              " and a.add_time <= '{end}' and b.pay_id = '{pay}'"\
            .format(shop=shop_code,start=start,end=end,pay=pay_id)

    cur.execute(sql)
    List = cur.fetchall()

    for item in List:
        if item['pay_value']:
            item['pay_value'] = float(item['pay_value'])
        else:
            item['pay_value'] = 0

    return render(request, 'report/card/saleGroupByShop/Detail.html', locals())

def date_detail(request):
    shop = mth.getReqVal(request, 'shopcode','')
    start = mth.getReqVal(request, 'start','')
    end = mth.getReqVal(request, 'end','')
    endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))
    page = mth.getReqVal(request, 'page', 1)

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    sale_sql = "select DATE_FORMAT(a.add_time, '%Y-%m-%d') as add_time,b.pay_id,sum(b.pay_value) as pay_value " \
               " from orders as a, order_payment_info as b" \
               " where a.order_sn = b.order_id and a.add_time>='{start}' and a.add_time<='{end}' and a.shop_code ='{shop}'" \
               " group by DATE_FORMAT(a.add_time, '%Y-%m-%d'),b.pay_id" \
                .format(start=start,end=endTime,shop=shop)
    cur.execute(sale_sql)
    data_sale = cur.fetchall()

    sale_disc_sql="select DATE_FORMAT(add_time, '%Y-%m-%d') as add_time," \
                  "SUM(case when disc_amount>=y_cash then disc_amount else diff_price+disc_amount end) as disc, " \
                  "SUM(y_cash) as disc_cash,"  \
                  "SUM(case when disc_amount>=y_cash then disc_amount-y_cash else disc_amount+diff_price-y_cash end) as disc_card " \
                  "from orders " \
                  "where add_time>='{start}' and add_time<='{end}' and shop_code ='{shop}' "  \
                  "group by DATE_FORMAT(add_time, '%Y-%m-%d') " \
                    .format(start=start, end=endTime, shop=shop)
    cur.execute(sale_disc_sql)
    data_sale_disc = cur.fetchall()

    change_sql = "select DATE_FORMAT(a.add_time, '%Y-%m-%d') as add_time,b.pay_id,sum(b.pay_value) as pay_value " \
               " from order_change_card as a, order_change_card_payment as b" \
               " where a.order_sn = b.order_id and a.add_time>='{start}' and a.add_time<='{end}' and a.shop_code ='{shop}'" \
               " group by DATE_FORMAT(a.add_time, '%Y-%m-%d'),b.pay_id" \
                .format(start=start,end=endTime,shop=shop)
    cur.execute(change_sql)
    data_change = cur.fetchall()

    change_disc_sql = "select DATE_FORMAT(add_time, '%Y-%m-%d') as add_time," \
                      "SUM(case when disc>=disc_cash then disc else disc_pay+disc end) as disc," \
                    "SUM(disc_cash) as disc_cash," \
                    "SUM(case when disc>=disc_cash then disc-disc_cash else disc+disc_pay-disc_cash end) as disc_card " \
                    "from order_change_card " \
                    "where add_time>='{start}' and add_time<='{end}' and shop_code ='{shop}' " \
                    "group by  DATE_FORMAT(add_time, '%Y-%m-%d') " \
        .format(start=start, end=endTime, shop=shop)
    cur.execute(change_disc_sql)
    data_change_disc = cur.fetchall()

    fill_sql = "select DATE_FORMAT(add_time, '%Y-%m-%d') as add_time,sum(diff_price) as pay_value" \
               " from order_up_card" \
               " where add_time>='{start}' and add_time<='{end}' and shop_code ='{shop}'" \
               " group by  DATE_FORMAT(add_time, '%Y-%m-%d') " \
                .format(start=start, end=endTime, shop=shop)
    cur.execute(fill_sql)
    data_fill = cur.fetchall()

    dates = mth.dateRange(start,end)

    res_list = []
    paymentsRate = Payment.objects.values('id', 'dis_rate').filter(dis_rate__gte=0)
    paymentsRateDict = {item['id']: float(item['dis_rate']) for item in paymentsRate}
    for date in dates:
        item = {'date': '',
                'disc': 0, 'disc_6': 0, 'disc_7': 0, 'disc_8': 0, 'disc_10': 0, 'disc_11': 0, 'disc_cash': 0,
                'disc_card': 0,
                'inSub': 0, 'pay_1': 0, 'pay_2': 0, 'pay_3': 0, 'pay_4': 0, 'pay_5': 0, 'pay_6': 0, 'pay_7': 0,
                'pay_8': 0,
                'pay_9': 0, 'pay_10': 0, 'pay_11': 0, }
        item['date'] = date
        for sale in data_sale:
            if sale['add_time'] == date:
                # 横向各门店售卡汇总赋值
                # pay_id = sale['pay_id']
                if sale['pay_id'] == 1:
                    item['pay_1'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 2:
                    item['pay_2'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 3:
                    item['pay_3'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 4:
                    item['pay_4'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 5:
                    item['pay_5'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 6:
                    item['pay_6'] += float(sale['pay_value'])
                    item['disc_6'] += float(sale['pay_value']) * paymentsRateDict[6]
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 7:
                    item['pay_7'] += float(sale['pay_value'])
                    item['disc_7'] += float(sale['pay_value']) * paymentsRateDict[7]
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 8:
                    item['pay_8'] += float(sale['pay_value'])
                    item['disc_8'] += float(sale['pay_value']) * paymentsRateDict[8]
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 9:
                    item['pay_9'] += float(sale['pay_value'])
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 10:
                    item['pay_10'] += float(sale['pay_value'])
                    item['disc_10'] += float(sale['pay_value']) * paymentsRateDict[10]
                    item['inSub'] += float(sale['pay_value'])
                if sale['pay_id'] == 11:
                    item['pay_11'] += float(sale['pay_value'])
                    item['disc_11'] += float(sale['pay_value']) * paymentsRateDict[11]
                    item['inSub'] += float(sale['pay_value'])

        for saleDisc in data_sale_disc:
            if saleDisc['add_time'] == date:
                if not saleDisc['disc']:
                    saleDisc['disc'] = 0
                if not saleDisc['disc_cash']:
                    saleDisc['disc_cash'] = 0
                if not saleDisc['disc_card']:
                    saleDisc['disc_card'] = 0
                item['disc'] += float(saleDisc['disc'])
                item['disc_cash'] += float(saleDisc['disc_cash'])
                item['disc_card'] += float(saleDisc['disc_card'])

        for fill in data_fill:
            if fill['add_time'] == date:
                if not fill['pay_value']:
                    fill['pay_value'] = 0

                item['pay_1'] += float(fill['pay_value'])
                item['inSub'] += float(fill['pay_value'])

        for change in data_change:
            if change['add_time'] == date:
                # 横向各门店售卡汇总赋值
                if change['pay_id'] == 1:
                    item['pay_1'] += float(change['pay_value'])
                if change['pay_id'] == 2:
                    item['pay_2'] += float(change['pay_value'])
                if change['pay_id'] == 3:
                    item['pay_3'] += float(change['pay_value'])
                if change['pay_id'] == 5:
                    item['pay_5'] += float(change['pay_value'])
                if change['pay_id'] == 6:
                    item['pay_6'] += float(change['pay_value'])
                    item['disc_6'] += float(change['pay_value']) * paymentsRateDict[6]
                if change['pay_id'] == 7:
                    item['pay_7'] += float(change['pay_value'])
                    item['disc_7'] += float(change['pay_value']) * paymentsRateDict[7]
                if change['pay_id'] == 8:
                    item['pay_8'] += float(change['pay_value'])
                    item['disc_8'] += float(change['pay_value']) * paymentsRateDict[8]
                if change['pay_id'] == 9:
                    item['pay_9'] += float(change['pay_value'])
                if change['pay_id'] == 10:
                    item['pay_10'] += float(change['pay_value'])
                    item['disc_10'] += float(change['pay_value']) * paymentsRateDict[10]
                if change['pay_id'] == 11:
                    item['pay_11'] += float(change['pay_value'])
                    item['disc_11'] += float(change['pay_value']) * paymentsRateDict[11]

                item['inSub'] += float(change['pay_value'])

        for changeDisc in data_change_disc:
            if changeDisc['add_time'] == date:
                if not changeDisc['disc']:
                    changeDisc['disc'] = 0
                if not changeDisc['disc_cash']:
                    changeDisc['disc_cash'] = 0
                if not changeDisc['disc_card']:
                    changeDisc['disc_card'] = 0
                item['disc'] += float(changeDisc['disc'])
                item['disc_cash'] += float(changeDisc['disc_cash'])
                item['disc_card'] += float(changeDisc['disc_card'])
        res_list.append(item)

    # 表单分页开始
    paginator = Paginator(res_list, 31)

    try:
        List = paginator.page(page)

        if List.number > 1:
            page_up = List.previous_page_number
        else:
            page_up = 1

        if List.number < List.paginator.num_pages:
            page_down = List.next_page_number
        else:
            page_down = List.paginator.num_pages

    except Exception as e:
        print(e)
    # 表单分页结束
    return render(request, 'report/card/saleGroupByShop/DateDetail.html', locals())