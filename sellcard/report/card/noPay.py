# -*-  coding:utf-8 -*-
import datetime
from django.shortcuts import render

from operator import itemgetter,attrgetter
from sellcard.common import Method as mth
from sellcard import views as base

def order(request):
    today = datetime.date.today()
    today = datetime.datetime.strftime(today, '%Y-%m-%d')

    shop = mth.getReqVal(request,'shop','')
    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    startTime = start + ' 00:00:00'
    endTime = end + ' 23:59:59'

    conn = mth.getMysqlConn()
    cur = conn.cursor()

    saleSql = 'select a.order_sn,a.buyer_company,b.is_pay,b.pay_value as no_pay,' \
              'c.bank_name,c.pay_value,c.pay_id,c.bank_sn,c.pay_company,c.change_time ' \
              'from orders as a inner join order_payment_info as b on a.order_sn = b.order_id left join order_payment_credit as c on a.order_sn = c.order_id '\
              'where a.add_time>="{start}" and a.add_time<="{end}" and a.shop_code ="{shop}" and b.pay_id=4 ' \
              'order by b.is_pay,a.order_sn' \
              .format(start=startTime, end=endTime, shop=shop)

    cur.execute(saleSql)
    saleList = cur.fetchall()
    saleData,saleTotalPay,saleTotalNoPay= mergeData(saleList)


    data = saleData
    totalPay = saleTotalPay
    totalNoPay = saleTotalNoPay
    data = sorted(data,key=itemgetter('is_pay','order_sn'),reverse=True)
    return render(request, 'report/card/nopay/order.html', locals())

def order2(request):
    shops = base.findShop()
    today = datetime.date.today()
    monthFirst = str(datetime.date.today().replace(day=1))
    today = str(today)

    shop = mth.getReqVal(request, 'shop', '')
    start = mth.getReqVal(request, 'start', monthFirst)
    end = mth.getReqVal(request, 'end', today)
    startTime = start + ' 00:00:00'
    endTime = end + ' 23:59:59'
    whereShop ='a.shop_code ="'+shop+'" ' if shop  else '1=1'

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    saleSql = 'select a.order_sn,a.shop_code,a.add_time,a.buyer_company,b.pay_value,b.received_time,c.change_time ' \
              ' from orders as a inner join order_payment_info as b on a.order_sn = b.order_id left join order_payment_credit as c on a.order_sn = c.order_id ' \
              ' where a.add_time>="{start}" and a.add_time<="{end}" and b.pay_id=4 and {whereShop}' \
              ' order by a.order_sn' \
        .format(start=startTime, end=endTime,whereShop=whereShop)

    cur.execute(saleSql)
    listSale = cur.fetchall()

    cur.close()
    conn.close()
    return render(request, 'report/card/nopay/order2.html', locals())

#列转行
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
                #原始赊销金额
                old_value = float(obj['no_pay'])
                #赊销还款金额
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
    return data,totalPay,totalNoPay


def month(request):
    """
    :param request:
    :return:
    """
    shops = mth.getCityShopsCode()
    if request.method == 'POST':
        postStart = request.POST.get('start')
        if postStart<'2017-06':
            postStart = '2017-06'
        postEnd = request.POST.get('end')

        start = '{postStart}-01 00:00:00'.format(postStart=postStart)
        endTemp = datetime.datetime.strptime(postEnd,'%Y-%m')
        if endTemp.month == 12:
            end = datetime.datetime(endTemp.year+1, 1, 1)
        else:
            end = datetime.datetime(endTemp.year, endTemp.month + 1, 1)

        shop_code = request.POST.get('shop','')
        parameterShop = '1=1'
        if shop_code:
            parameterShop = 'a.shop_code="{shop}"'.format(shop=shop_code)

        conn = mth.getMysqlConn()
        cur = conn.cursor()

        #在起始日期之前赊销，在起始日期之前未到账
        sqlBeforeNoPay = 'select sum(b.pay_value) as total from orders as a, order_payment_info as b' \
                         ' where a.add_time>="2017-06-01 00:00:00" and a.add_time<="{start}" and {shop}' \
                         ' and b.pay_id in (4,6) and is_pay=0 and a.order_sn = b.order_id' \
                        .format(start=start,shop=parameterShop)
        cur.execute(sqlBeforeNoPay)
        beforeNoPay1 = cur.fetchone()
        totalNoPayBefore1 = beforeNoPay1['total']
        totalNoPayBefore1 = totalNoPayBefore1 if totalNoPayBefore1 else 0
        #在起始日期之前赊销，在起始日期之后到账
        sqlBeforeNoPay2 = 'select sum(b.pay_value) as total from order_payment_credit as b LEFT JOIN orders as a ' \
        'ON b.order_id = a.order_sn ' \
        'where a.add_time>="2017-06-01 00:00:00" and a.add_time<="{start}" and b.change_time>="{start}" and {shop} and b.pay_id_old in (4,6)' \
        .format(start=start, end=end, shop=parameterShop)

        cur.execute(sqlBeforeNoPay2)
        beforeNoPay2 = cur.fetchone()
        totalNoPayBefore2 = beforeNoPay2['total']
        totalNoPayBefore2 = totalNoPayBefore2 if totalNoPayBefore2 else 0

        totalNoPayBefore = totalNoPayBefore1 +totalNoPayBefore2

        sqlNoPay = 'select a.order_sn,a.buyer_company,a.shop_code,a.add_time,b.pay_id ,b.pay_value ' \
                  'from orders as a,order_payment_info as b ' \
                  'where a.add_time>="{start}" and a.add_time<="{end}" and {shop} ' \
                  'and (b.pay_id in (4,6) or b.change_time>0) and a.order_sn = b.order_id ' \
                  'order by a.add_time'.format(start=start, end=end,shop=parameterShop)
        cur.execute(sqlNoPay)
        noPayList = cur.fetchall()
        sqlPaid = 'select a.order_sn,a.shop_code,b.pay_company,b.change_time,b.pay_id ,b.pay_value ' \
                  'from order_payment_credit as b LEFT JOIN orders as a ' \
                  'ON b.order_id = a.order_sn ' \
                  'where a.add_time>="2017-06-01 00:00:00" and b.change_time>="{start}" and {shop}' \
                  ' and b.change_time<="{end}" and b.pay_id_old!=3 ' \
                  'order by b.change_time'.format(start=start, end=end,shop=parameterShop)
        cur.execute(sqlPaid)
        paidList = cur.fetchall()

        noPayList = splitData('0',noPayList,start,end)
        paidList = splitData('1',paidList,start,end)
        dataSelect = noPayList + paidList
        totalNoPay = float(totalNoPayBefore)
        if len(dataSelect)>0:
            dataSorted = sorted(dataSelect, key=itemgetter('time'), reverse=False)
            totalPay,MonthNoPay,MonthPay,index, = 0,0,0,0
            resData,monthSubTimeList = [],[]

            for row in dataSorted:
                rowTimeNow = row['time']
                rowTimePre = dataSorted[index-1]['time']
                if isNextMonth(rowTimeNow,rowTimePre) and (row['time'].date()+datetime.timedelta(days=-1) not in monthSubTimeList):
                    time = datetime.datetime(rowTimeNow.year,rowTimeNow.month,1)+datetime.timedelta(days=-1)
                    if time>=datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S'):
                        monthSubitem = MonthSub(MonthPay,MonthNoPay,time)
                        resData.insert(index+1,monthSubitem)
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

            #最后一行月度合计
            lastDataTime = resData[len(resData)-1]['time']
            if lastDataTime.month == 12:
                lastMonthSubTime = datetime.datetime(lastDataTime.year+1, 1, 1) + datetime.timedelta(-1)
            else:
                lastMonthSubTime = datetime.datetime(lastDataTime.year, lastDataTime.month + 1, 1)+datetime.timedelta(-1)
            if lastMonthSubTime not in monthSubTimeList:
                monthSubitem = MonthSub(MonthPay, MonthNoPay, lastMonthSubTime)
                resData.append(monthSubitem)
                monthSubTimeList.append(lastMonthSubTime)
                MonthNoPay = 0
                MonthPay = 0

    return render(request, 'report/card/nopay/month.html', locals())


def month_pay4(request):
    """
    :param request:
    :return:
    """
    shops = mth.getCityShopsCode()
    if request.method == 'POST':
        postStart = request.POST.get('start')
        if postStart<'2017-06':
            postStart = '2017-06'
        postEnd = request.POST.get('end')

        start = '{postStart}-01 00:00:00'.format(postStart=postStart)
        endTemp = datetime.datetime.strptime(postEnd,'%Y-%m')
        if endTemp.month == 12:
            end = datetime.datetime(endTemp.year+1, 1, 1)
        else:
            end = datetime.datetime(endTemp.year, endTemp.month + 1, 1)

        shop_code = request.POST.get('shop','')
        parameterShop = '1=1'
        if shop_code:
            parameterShop = 'a.shop_code="{shop}"'.format(shop=shop_code)

        conn = mth.getMysqlConn()
        cur = conn.cursor()

        #在起始日期之前赊销，在起始日期之前未到账
        sqlBeforeNoPay = 'select sum(b.pay_value) as total from orders as a, order_payment_info as b' \
                         ' where a.add_time>="2017-06-01 00:00:00" and a.add_time<="{start}" and {shop}' \
                         ' and b.pay_id =4 and is_pay=0 and a.order_sn = b.order_id' \
                        .format(start=start,shop=parameterShop)
        cur.execute(sqlBeforeNoPay)
        beforeNoPay1 = cur.fetchone()
        totalNoPayBefore1 = beforeNoPay1['total']
        totalNoPayBefore1 = totalNoPayBefore1 if totalNoPayBefore1 else 0
        #在起始日期之前赊销，在起始日期之后到账
        sqlBeforeNoPay2 = 'select sum(b.pay_value) as total' \
                          ' from order_payment_credit as b LEFT JOIN orders as a ON b.order_id = a.order_sn' \
                          ' where a.add_time>="2017-06-01 00:00:00" and a.add_time<="{start}"' \
                          ' and b.change_time>="{start}" and {shop} and b.pay_id_old =4' \
                          .format(start=start, end=end, shop=parameterShop)
        cur.execute(sqlBeforeNoPay2)
        beforeNoPay2 = cur.fetchone()
        totalNoPayBefore2 = beforeNoPay2['total']
        totalNoPayBefore2 = totalNoPayBefore2 if totalNoPayBefore2 else 0
        #历史累计
        totalNoPayBefore = totalNoPayBefore1 +totalNoPayBefore2

        #赊出记录
        sqlNoPay =' select a.order_sn,a.buyer_company,a.shop_code,a.add_time,b.pay_id ,b.pay_value' \
                  ' from orders as a,order_payment_info as b' \
                  ' where a.add_time>="2017-06-01 00:00:00" and a.add_time>="{start}" and a.add_time<="{end}" and {shop}' \
                  ' and b.pay_id =4 and a.order_sn = b.order_id' \
                  ' order by a.add_time'.format(start=start, end=end,shop=parameterShop)
        cur.execute(sqlNoPay)
        noPayList = cur.fetchall()
        #还款记录
        sqlPaid = ' select a.order_sn,a.shop_code,b.pay_company,b.change_time,b.pay_id ,b.pay_value' \
                  ' from order_payment_credit as b LEFT JOIN orders as a' \
                  ' ON b.order_id = a.order_sn' \
                  ' where a.add_time>="2017-06-01 00:00:00" and b.change_time>="{start}" and {shop}' \
                  ' and b.change_time<="{end}" and b.pay_id_old=4' \
                  ' order by b.change_time'.format(start=start, end=end,shop=parameterShop)
        cur.execute(sqlPaid)
        paidList = cur.fetchall()

        noPayList = splitData('0',noPayList,start,end)
        paidList = splitData('1',paidList,start,end)
        dataSelect = noPayList + paidList
        totalNoPay = float(totalNoPayBefore)
        if len(dataSelect)>0:
            dataSorted = sorted(dataSelect, key=itemgetter('time'), reverse=False)
            totalPay,MonthNoPay,MonthPay,index, = 0,0,0,0
            resData,monthSubTimeList = [],[]

            for row in dataSorted:
                rowTimeNow = row['time']
                rowTimePre = dataSorted[index-1]['time']
                if isNextMonth(rowTimeNow,rowTimePre) and (row['time'].date()+datetime.timedelta(days=-1) not in monthSubTimeList):
                    time = datetime.datetime(rowTimeNow.year,rowTimeNow.month,1)+datetime.timedelta(days=-1)
                    if time>=datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S'):
                        monthSubitem = MonthSub(MonthPay,MonthNoPay,time)
                        resData.append(monthSubitem)
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

            #最后一行月度合计
            lastDataTime = resData[len(resData)-1]['time']
            if lastDataTime.month == 12:
                lastMonthSubTime = datetime.datetime(lastDataTime.year+1, 1, 1) + datetime.timedelta(-1)
            else:
                lastMonthSubTime = datetime.datetime(lastDataTime.year, lastDataTime.month + 1, 1)+datetime.timedelta(-1)
            if lastMonthSubTime not in monthSubTimeList:
                monthSubitem = MonthSub(MonthPay, MonthNoPay, lastMonthSubTime)
                resData.append(monthSubitem)
                monthSubTimeList.append(lastMonthSubTime)
                MonthNoPay = 0
                MonthPay = 0

    return render(request, 'report/card/nopay/month_pay4.html', locals())


def month_pay6(request):
    """
    移动积分赊还款
    :param request:
    :return:
    """
    shops = mth.getCityShopsCode()
    if request.method == 'POST':
        postStart = request.POST.get('start')
        if postStart<'2017-01':
            postStart = '2017-01'
        postEnd = request.POST.get('end')

        start = '{postStart}-01 00:00:00'.format(postStart=postStart)
        endTemp = datetime.datetime.strptime(postEnd,'%Y-%m')
        if endTemp.month == 12:
            end = datetime.datetime(endTemp.year+1, 1, 1)
        else:
            end = datetime.datetime(endTemp.year, endTemp.month + 1, 1)

        shop_code = request.POST.get('shop','')
        parameterShop = '1=1'
        parameterShop2 = '1=1'
        if shop_code:
            parameterShop = 'shop="{shop}"'.format(shop=shop_code)
            parameterShop2 = 'shop_code="{shop}"'.format(shop=shop_code)

        conn = mth.getMysqlConn()
        cur = conn.cursor()

        #在起始日期之前赊销，在起始日期之前未到账
        sqlBeforeNoPay = ' select sum(b.pay_value) as total' \
                         ' from orders as a, order_payment_info as b' \
                         ' where a.add_time>="2017-01-01 00:00:00" and a.add_time<="{start}" and {shop}' \
                         ' and b.pay_id =6 and a.order_sn = b.order_id' \
                        .format(start=start,shop=parameterShop2)
        cur.execute(sqlBeforeNoPay)
        beforeNoPay = cur.fetchone()
        totalNoPayBefore = beforeNoPay['total']
        totalNoPayBefore = totalNoPayBefore if totalNoPayBefore else 0
        #在起始日期之前赊销，在起始日期之后到账
        sqlBeforePaid = 'select sum(b.pay_value) as total' \
                        ' from order_payment_credit as b,orders as a ' \
                        ' where a.order_sn=b.order_id and a.add_time>="2017-01-01 00:00:00" and a.add_time<="{start}"' \
                        ' and b.change_time>="{start}" and {shop} and b.pay_id_old =6' \
                        .format(start=start, end=end, shop=parameterShop2)
        cur.execute(sqlBeforePaid)
        beforePaid = cur.fetchone()
        totalPaidBefore = beforePaid['total']
        totalPaidBefore = totalPaidBefore if totalPaidBefore else 0
        #历史累计
        totalNoPayBefore = totalNoPayBefore - totalPaidBefore

        #赊出记录
        sqlNoPay =' select a.shop_code as shop,DATE_FORMAT(a.add_time,"%Y-%m") as add_time,SUM(b.pay_value) as pay_value,0 as is_pay' \
                  ' from orders as a,order_payment_info as b' \
                  ' where a.add_time>="2017-01-01 00:00:00" and a.add_time>="{start}" and a.add_time<="{end}" and {shop}' \
                  ' and b.pay_id =6 and a.order_sn = b.order_id' \
                  ' GROUP BY a.shop_code,DATE_FORMAT(a.add_time,"%Y-%m")'\
            .format(start=start, end=end,shop=parameterShop2)
        cur.execute(sqlNoPay)
        noPayList = cur.fetchall()
        #还款记录
        sqlPaid = ' select shop,DATE_FORMAT(change_time,"%Y-%m") as change_time,sum(pay_value) as pay_value,1 is_pay' \
                  ' from order_payment_credit ' \
                  ' where change_time>="2017-01-01 00:00:00" and change_time>="{start}" and change_time<="{end}"' \
                  ' and {shop} and pay_id_old=6' \
                  ' GROUP BY shop,DATE_FORMAT(change_time,"%Y-%m")'.format(start=start, end=end,shop=parameterShop)
        cur.execute(sqlPaid)
        paidList = cur.fetchall()
        noPayList = splitDataPay6('0', noPayList, start, end)
        paidList = splitDataPay6('1', paidList, start, end)
        dataSelect = noPayList + paidList
        totalNoPay = float(totalNoPayBefore)
        if len(dataSelect) > 0:
            dataSorted = sorted(dataSelect, key=itemgetter('time'), reverse=False)
            totalPay, MonthNoPay, MonthPay, index, = 0, 0, 0, 0
            resData, monthSubTimeList = [], []

            for row in dataSorted:
                rowTimeNow = datetime.datetime.strptime(row['time'],'%Y-%m')
                if index == 0:
                    rowTimePre =rowTimeNow
                else:
                    rowTimePre = dataSorted[index - 1]['time']
                    rowTimePre = datetime.datetime.strptime(rowTimePre,'%Y-%m')
                if isNextMonth(rowTimeNow, rowTimePre) and (rowTimeNow.date() + datetime.timedelta(days=-1) not in monthSubTimeList):
                    preMonthEnd = datetime.datetime(rowTimeNow.year, rowTimeNow.month, 1) + datetime.timedelta(days=-1)
                    startDate = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                    if preMonthEnd >= startDate:
                        monthSubitem = MonthSub(MonthPay, MonthNoPay, preMonthEnd.date())
                        resData.append(monthSubitem)
                        monthSubTimeList.append(preMonthEnd)
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
            lastDataTime = datetime.datetime.strptime(lastDataTime,'%Y-%m')
            if lastDataTime.month == 12:
                lastMonthSubTime = datetime.datetime(lastDataTime.year + 1, 1, 1) + datetime.timedelta(-1)
            else:
                lastMonthSubTime = datetime.datetime(lastDataTime.year, lastDataTime.month + 1, 1) + datetime.timedelta(-1)
            if lastMonthSubTime not in monthSubTimeList:
                monthSubitem = MonthSub(MonthPay, MonthNoPay, lastMonthSubTime.date())
                resData.append(monthSubitem)
                monthSubTimeList.append(lastMonthSubTime)
                MonthNoPay = 0
                MonthPay = 0


    return render(request, 'report/card/nopay/month_pay6.html', locals())



def splitData(flag,dataList,start,end):
    """
    将起止日期之前的数据，进行到账与未到账的分离
    :param dataList: 数据列表
    :param start: 起始月份
    :param end: 截至日月
    :return: list
    """
    data = []
    if flag == '1':
        payList = base.findPays()
        payDict = {pay['id']: pay['payment_name'] for pay in payList}
        for order in dataList:
            itemPay = createPayRow(payDict,order, end)
            if itemPay:
                data.append(itemPay)
            # if order['add_time'] >= datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'):
            #     # 创建赊销记录
            #     itemNoPay = createNoPayRow(order)
            #     data.append(itemNoPay)
    else:
        for order in dataList:
            itemNoPay = createNoPayRow(order)
            data.append(itemNoPay)
    # for order in dataList:
    #     if order['is_pay'] == '1':
    #         itemPay = createPayRow(order, end)
    #         if itemPay:
    #             data.append(itemPay)
    #         if order['add_time'] >= datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'):
    #             # 创建赊销记录
    #             itemNoPay = createNoPayRow(order)
    #             data.append(itemNoPay)
    #     else:
    #         itemNoPay = createNoPayRow(order)
    #         data.append(itemNoPay)
    return data


def splitDataPay6(flag,dataList,start,end):
    """
    将起止日期之前的数据，进行到账与未到账的分离
    :param dataList: 数据列表
    :param start: 起始月份
    :param end: 截至日月
    :return: list
    """
    data = []
    if flag == '1':
        payList = base.findPays()
        payDict = {pay['id']: pay['payment_name'] for pay in payList}
        for order in dataList:
            itemPay = createPayRowPay6(payDict,order, end)
            if itemPay:
                data.append(itemPay)
    else:
        for order in dataList:
            itemNoPay = createNoPayRowPay6(order)
            data.append(itemNoPay)
    return data


def splitDataBefore(dataList,start,end):
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
            itemPay = createPayRow(order, datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S'))
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
    return  item


def createNoPayRowPay6(obj):
    """
    创建赊销未到账记录
    :param obj:
    :return:
    """
    item = {}
    item['time'] = obj['add_time']
    item['shop'] = obj['shop']
    item['noPay'] = obj['pay_value']
    item['is_pay'] = '0'
    return  item


def createPayRow(payDict,obj,time):
    """
    创建赊销到账记录
    :param obj:
    :param time:
    :return:
    """

    if obj['change_time']<time:
        item = {}
        item['time'] = obj['change_time']
        item['sn'] = obj['order_sn']
        pay_id = obj['pay_id']
        if obj['pay_company']:
            info = '赊销到账：' +payDict[pay_id]+ '('+obj['pay_company']+')'
        else:
            info = '赊销到账: '+payDict[pay_id]
        item['info'] = info
        item['shop'] = obj['shop_code']
        item['pay'] = obj['pay_value']
        item['is_pay'] = '1'
        return item


def createPayRowPay6(payDict,obj,time):
    """
    创建赊销到账记录
    :param obj:
    :param time:
    :return:
    """
    if datetime.datetime.strptime(obj['change_time'],'%Y-%m')<time:
        item = {}
        item['time'] = obj['change_time']
        item['shop'] = obj['shop']
        item['pay'] = obj['pay_value']
        item['is_pay'] = '1'
        return item


def MonthSub(MonthPay,MonthNoPay,time):
    item = {}
    item['info'] = '月度合计'
    item['pay'] = MonthPay
    item['noPay'] = MonthNoPay
    item['sub'] = ''
    item['time'] = time
    item['monthSub'] = True
    return item


def isNextMonth(rowTimeNow,rowTimePre):
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
    if rowYearNow > rowYearPre :
        return True
    elif rowYearNow == rowYearPre:
        if rowMonthNow > rowMonthPre:
            return True
        else:
            return None
