# -*-  coding:utf-8 -*-
from django.shortcuts import render
from operator import itemgetter, attrgetter
import datetime
from sellcard.common import Method as mth
from sellcard import views as base


def order(request):
    shop = request.GET.get('shop')
    today = datetime.date.today()
    start = request.GET.get('start', today)
    end = request.GET.get('end', today)
    endTime = str(datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1))
    conn = mth.getMysqlConn()
    cur = conn.cursor()

    # 售卡数据
    saleSql = 'select a.order_sn,a.buyer_company,b.is_pay,b.pay_value as no_pay,c.bank_name,c.pay_value,c.pay_id,c.bank_sn,c.pay_company,c.change_time ' \
              'from orders as a inner join order_payment_info as b on a.order_sn = b.order_id left join order_payment_credit as c on a.order_sn = c.order_id ' \
              'where a.add_time>="{start}" and a.add_time<="{end}" and a.shop_code ="{shop}" and b.pay_id=4 ' \
              'order by b.is_pay,a.order_sn' \
        .format(start=start, end=endTime, shop=shop)
    cur.execute(saleSql)
    saleList = cur.fetchall()
    saleData, saleTotalPay, saleTotalNoPay = mergeData(saleList)

    data = saleData
    totalPay = saleTotalPay
    totalNoPay = saleTotalNoPay
    data = sorted(data, key=itemgetter('is_pay', 'order_sn'), reverse=True)
    return render(request, 'report/card/nopay/order.html', locals())


# 列转行
def mergeData(List):
    OrderSnList = [item['order_sn'] for item in List]
    OrderSnSet = list(set(OrderSnList))
    totalPay = 0
    totalNoPay = 0
    data = []
    for sn in OrderSnSet:
        item = {}
        item['orderNoPay'] = 0
        item['order_sn'] = sn
        for obj in List:
            if obj['order_sn'] == sn:
                item['is_pay'] = obj['is_pay']
                item['depart'] = obj['buyer_company']
                item['change_time'] = obj['change_time']
                # 原始赊销金额
                old_value = float(obj['no_pay'])
                # 赊销还款金额
                pay_value = float(obj['pay_value']) if obj['pay_value'] else 0
                if obj['is_pay'] == '1':
                    totalPay += pay_value
                    if obj['pay_id'] == 1:
                        item['cash'] = pay_value
                    if obj['pay_id'] == 3:
                        item['bank'] = pay_value
                        item['bank_name'] = obj['bank_name']
                        item['bank_sn'] = obj['bank_sn']
                        item['pay_company'] = obj['pay_company']
                    if obj['pay_id'] == 5:
                        item['pos'] = pay_value
                else:
                    totalNoPay += old_value
                    item['orderNoPay'] += old_value
        data.append(item)
    return data, totalPay, totalNoPay


def month(request):
    if request.method == 'POST':
        postStart = request.POST.get('start')
        postEnd = request.POST.get('end')

        start = '{postStart}-01 00:00:00'.format(postStart=postStart)
        endTemp = datetime.datetime.strptime(postEnd, '%Y-%m')
        if endTemp.month == 12:
            end = datetime.datetime(endTemp.year + 1, 1, 1)
        else:
            end = datetime.datetime(endTemp.year, endTemp.month + 1, 1)

        conn = mth.getMysqlConn()
        cur = conn.cursor()
        # 查询：起始日期之前的历史数据
        noPayBeforeSql = 'select a.order_sn,a.buyer_company,a.shop_code,a.add_time,b.pay_id ,b.pay_value,b.change_time,b.bank_name,b.bank_sn,b.pay_company,b.is_pay ' \
                         'from orders as a , order_payment_info as b ' \
                         'where ((a.add_time<="{start}"  and b.pay_id=4) or (b.change_time<="{start}")) ' \
                         'and a.order_sn = b.order_id ' \
                         'order by a.add_time' \
            .format(start=start, end=end)
        cur.execute(noPayBeforeSql)
        noPayBeforeList = cur.fetchall()
        # 分离数据
        dataBefore = splitDataBefore(noPayBeforeList, start, end)

        # 计算：起始日期之前，未到账数据总和
        totalNoPayBefore = 0
        for row in dataBefore:
            if 'is_pay' in row:
                if row['is_pay'] == '1':
                    totalNoPayBefore += -float(row['pay'])
                else:
                    totalNoPayBefore += float(row['noPay'])

        # 查询：起止时间段内的数据
        noPayOrderSql = 'select a.order_sn,a.buyer_company,a.shop_code,a.add_time,b.pay_id ,b.pay_value,b.change_time,b.bank_name,b.bank_sn,b.pay_company,b.is_pay ' \
                        'from orders as a , order_payment_info as b ' \
                        'where ((a.add_time>="{start}" and a.add_time<="{end}" and b.pay_id=4) or (b.change_time>="{start}" and b.change_time<="{end}")) ' \
                        'and a.order_sn = b.order_id ' \
                        'order by a.add_time' \
            .format(start=start, end=end)
        cur.execute(noPayOrderSql)
        noPayOrderList = cur.fetchall()
        # 分离数据
        dataSelect = splitData(noPayOrderList, start, end)
        dataSorted = sorted(dataSelect, key=itemgetter('time'), reverse=False)

        totalNoPay = float(totalNoPayBefore)
        totalPay, MonthNoPay, MonthPay, index, = 0, 0, 0, 0
        resData, monthSubTimeList = [], []

        for row in dataSorted:
            rowTimeNow = row['time']
            rowTimePre = dataSorted[index - 1]['time']
            #
            if isNextMonth(rowTimeNow, rowTimePre) and (
                    row['time'].date() + datetime.timedelta(days=-1) not in monthSubTimeList):
                time = datetime.datetime(rowTimeNow.year, rowTimeNow.month, 1) + datetime.timedelta(days=-1)
                if time >= datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'):
                    monthSubitem = MonthSub(MonthPay, MonthNoPay, time)
                    resData.insert(index + 1, monthSubitem)
                    monthSubTimeList.append(time)
                    MonthNoPay = 0
                    MonthPay = 0
            if 'is_pay' in row:
                if row['is_pay'] == '1':
                    MonthPay += float(row['pay'])
                    totalPay += float(row['pay'])
                    totalNoPay += -float(row['pay'])
                    row['sub'] = totalNoPay
                else:
                    MonthNoPay += float(row['noPay'])
                    totalNoPay += float(row['noPay'])
                    row['sub'] = totalNoPay
                resData.append(row)

            index += 1

        # 最后一行月度合计
        lastDataTime = resData[len(resData) - 1]['time']
        if lastDataTime.month == 12:
            lastMonthSubTime = datetime.datetime(lastDataTime.year + 1, 1, 1) + datetime.timedelta(-1)
        else:
            lastMonthSubTime = datetime.datetime(lastDataTime.year, lastDataTime.month + 1, 1) + datetime.timedelta(-1)
        if lastMonthSubTime not in monthSubTimeList:
            monthSubitem = MonthSub(MonthPay, MonthNoPay, lastMonthSubTime)
            resData.append(monthSubitem)
            monthSubTimeList.append(lastMonthSubTime)
            MonthNoPay = 0
            MonthPay = 0

    return render(request, 'report/card/nopay/month.html', locals())


def splitData(dataList, start, end):
    """
    将起止日期之前的数据，进行到账与未到账的分离
    :param dataList: 数据列表
    :param start: 起始月份
    :param end: 截至日月
    :return: list
    """
    data = []
    for order in dataList:
        if order['is_pay'] == '1':
            itemPay = createPayRow(order, end)
            if itemPay:
                data.append(itemPay)
            if order['add_time'] >= datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'):
                # 创建赊销记录
                itemNoPay = createNoPayRow(order)
                data.append(itemNoPay)
        else:
            itemNoPay = createNoPayRow(order)
            data.append(itemNoPay)
    return data


def splitDataBefore(dataList, start, end):
    """
    将起始日期之前的数据，进行到账与未到账的分离
    :param dataList: 数据列表
    :param start: 起始月份
    :param end: 截至日月
    :return: list
    """
    data = []
    for order in dataList:
        if order['is_pay'] == '1':
            itemPay = createPayRow(order, datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'))
            if itemPay:
                data.append(itemPay)
            if order['add_time'] < datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'):
                itemNoPay = createNoPayRow(order)
                data.append(itemNoPay)
        else:
            itemNoPay = createNoPayRow(order)
            data.append(itemNoPay)
    return data


def createNoPayRow(obj):
    """
    创建赊销未到账记录
    :param obj:
    :return:
    """
    item = {}
    item['time'] = obj['add_time']
    item['sn'] = obj['order_sn']
    buyer_company = obj['buyer_company'] if obj['buyer_company'] else '未填写'
    item['info'] = '赊销单位：' + buyer_company
    item['shop'] = obj['shop_code']
    item['noPay'] = obj['pay_value']
    item['is_pay'] = '0'
    return item


def createPayRow(obj, time):
    """
    创建赊销到账记录
    :param obj:
    :param time:
    :return:
    """
    payList = base.findPays()
    payDict = {pay['id']: pay['payment_name'] for pay in payList}
    if obj['change_time'] < time:
        item = {}
        item['time'] = obj['change_time']
        item['sn'] = obj['order_sn']
        pay_id = obj['pay_id']
        if obj['pay_company']:
            info = '赊销到账：' + payDict[pay_id] + '(' + obj['pay_company'] + ')'
        else:
            info = '赊销到账: ' + payDict[pay_id]
        item['info'] = info
        item['shop'] = obj['shop_code']
        item['pay'] = obj['pay_value']
        item['is_pay'] = '1'
        return item


def MonthSub(MonthPay, MonthNoPay, time):
    item = {}
    item['info'] = '月度合计'
    item['pay'] = MonthPay
    item['noPay'] = MonthNoPay
    item['sub'] = ''
    item['time'] = time
    item['monthSub'] = True
    return item


def isNextMonth(rowTimeNow, rowTimePre):
    """
    判断是否月初
    :param rowTimeNow: 本条数据的日期
    :param rowTimePre: 行一条数据的日期
    :return: bool
    """
    rowYearNow = rowTimeNow.year
    rowYearPre = rowTimePre.year
    rowMonthNow = rowTimeNow.month
    rowMonthPre = rowTimePre.month
    if rowYearNow > rowYearPre:
        return True
    if rowYearNow == rowYearPre:
        if rowMonthNow > rowMonthPre:
            return True
    else:
        return None
