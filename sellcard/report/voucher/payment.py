#-*- coding:utf-8 -*-
__author__ = 'qixu'
import datetime
from operator import itemgetter

from django.shortcuts import render

from sellcard.models import Shops
from sellcard.common import Method as mth

def index(request):
    """
       购物券销售汇总controllers
       :param request:
       :return:列表view
    """
    shop = request.session.get('s_shopcode', '')
    role = request.session.get('s_roleid')
    start = ''
    end = ''
    endTime = ''
    if request.method == 'GET':
        start = str(datetime.date.today().replace(day=1))
        end = str(datetime.date.today())
        endTime = str(datetime.date.today() + datetime.timedelta(1))
    if request.method == 'POST':
        today = datetime.date.today()
        start = request.POST.get('start', today)
        end = request.POST.get('end', today)
        endTime = str(datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1))
    shops = Shops.objects.values('shop_code', 'city').order_by('shop_code')
    if role in ('1', '6', '7'):
        shops = shops
    elif role == '8':  # 承德总部财务
        shops = shops.filter(city='C')
    elif role == '9':  # 唐山总部财务
        shops = shops.filter(city='T')
    else:
        shops = shops.filter(shop_code=shop)
    code_list = []
    for item_shop in shops:
        code_list.append(item_shop['shop_code'])
    code_list = str(code_list)
    code_list = code_list.replace('[','').replace(']','')
    sql = u" SELECT jc.shop_code, " \
          u" IFNULL((SUM(jc.total_values)),0) AS total_values, " \
          u" IFNULL(SUM(jc.total_discount),0) AS total_discount, " \
          u" IFNULL(SUM(jc.cash),0) AS cash, " \
          u" IFNULL(SUM(jc.remit),0) AS remit, " \
          u" IFNULL(SUM(jc.pos),0) AS pos, " \
          u" IFNULL(SUM(jc.credit),0) AS credit, " \
          u" IFNULL(SUM(jcc.credit_cash),0) AS credit_cash, " \
          u" IFNULL(SUM(jcc.credit_remit),0) AS credit_remit, " \
          u" IFNULL(SUM(jcc.credit_pos),0) AS credit_pos, " \
          u" IFNULL(SUM(jc.cash),0) + IFNULL(SUM(jcc.credit_cash),0) AS total_cash, " \
          u" IFNULL(SUM(jc.remit),0) + IFNULL(SUM(jcc.credit_remit),0) AS total_remit, " \
          u" IFNULL(SUM(jc.pos),0) + IFNULL(SUM(jcc.credit_pos),0) AS total_pos, " \
          u" IFNULL(SUM(jc.cash),0) + IFNULL(SUM(jc.remit),0) + IFNULL(SUM(jc.pos),0) " \
          u" + IFNULL(SUM(jcc.credit_cash),0) + IFNULL(SUM(jcc.credit_remit),0) " \
          u" + IFNULL(SUM(jcc.credit_pos),0) AS total_account " \
          u" FROM(SELECT c.coupon_code, c.shop_code, " \
          u" c.amount * c.`values` AS total_values, " \
          u" c.amount * c.discount AS total_discount, " \
          u" CASE WHEN c.payment_type = 1 THEN c.pay_account ELSE 0 END AS cash, " \
          u" CASE WHEN c.payment_type = 3 THEN c.pay_account ELSE 0 END AS remit, " \
          u" CASE WHEN c.payment_type = 5 THEN c.pay_account ELSE 0 END AS pos, " \
          u" CASE WHEN c.payment_type = 4 THEN c.pay_account - c.credit_account ELSE 0 END AS credit " \
          u" FROM kf_jobs_coupon c " \
          u" WHERE c.shop_code IN ({shop_one}) " \
          u" AND c.start_date BETWEEN '{start_one}' AND '{end_one}' " \
          u" UNION SELECT c.coupon_code, c.shop_code, 0, 0, 0, 0, 0, 0 " \
          u" FROM kf_jobs_coupon c " \
          u" WHERE c.shop_code IN ({shop_two}) AND c.start_date < '{start_two}' ) jc " \
          u" LEFT JOIN ( SELECT cc.coupon_code, " \
          u" CASE WHEN cc.payment_type = 1 THEN cc.pay_account ELSE 0 END AS credit_cash, " \
          u" CASE WHEN cc.payment_type = 3 THEN cc.pay_account ELSE 0 END AS credit_remit, " \
          u" CASE WHEN cc.payment_type = 5 THEN cc.pay_account ELSE 0 END AS credit_pos " \
          u" FROM kf_jobs_coupon_credit cc " \
          u" WHERE cc.create_date BETWEEN '{start_three}' AND '{end_two}' ) jcc " \
          u" ON jc.coupon_code = jcc.coupon_code " \
          u" GROUP BY jc.shop_code ".format(shop_one=code_list,
                                            start_one=start,
                                            end_one=endTime,
                                            shop_two=code_list,
                                            start_two=start,
                                            start_three=start,
                                            end_two=endTime)
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    cur.execute(sql)
    List = cur.fetchall()
    cur.close()
    conn.close()
    list_len = len(List)

    if list_len > 1:
        total = {}
        total['total_values'] = 0
        total['total_discount'] = 0
        total['total_account'] = 0
        total['total_cash'] = 0
        total['cash'] = 0
        total['credit_cash'] = 0
        total['total_remit'] = 0
        total['remit'] = 0
        total['credit_remit'] = 0
        total['total_pos'] = 0
        total['pos'] = 0
        total['credit_pos'] = 0
        total['credit'] = 0
        for item in List:
            total['total_values'] += item['total_values']
            total['total_discount'] += item['total_discount']
            total['total_account'] += item['total_account']
            total['total_cash'] += item['total_cash']
            total['cash'] += item['cash']
            total['credit_cash'] += item['credit_cash']
            total['total_remit'] += item['total_remit']
            total['remit'] += item['remit']
            total['credit_remit'] += item['credit_remit']
            total['total_pos'] += item['total_pos']
            total['pos'] += item['pos']
            total['credit_pos'] += item['credit_pos']
            total['credit'] += item['credit']
    return render(request, 'report/voucher/payment/list.html', locals())

def detail(request):
    shop = request.session.get('s_shopcode', '')
    role = request.session.get('s_roleid')
    start = str(datetime.date.today().replace(day=1))
    end = str(datetime.date.today())
    endTime = str(datetime.date.today() + datetime.timedelta(1))


def pay_4(request):
    shops = mth.getCityShopsCode()
    if request.method == 'POST':
        start_post = request.POST.get('start','')
        end_post = request.POST.get('end','')
        shop_code = request.POST.get('shop', '')
        parameterShop = '1=1'
        if shop_code:
            parameterShop = 'shop_code="{shop}"'.format(shop=shop_code)

        start = '{start}-01 00:00:00'.format(start=start_post)
        endTemp = datetime.datetime.strptime(end_post, '%Y-%m')
        if endTemp.month == 12:
            end = datetime.datetime(endTemp.year + 1, 1, 1)
        else:
            end = datetime.datetime(endTemp.year, endTemp.month + 1, 1)

        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sql_before_paid = " select sum(b.pay_account) as paid" \
                     " from kf_jobs_coupon as a,kf_jobs_coupon_credit as b" \
                     " where a.coupon_code = b.coupon_code and DATE_FORMAT(a.create_date,'%Y-%m-%d')<='{start}'" \
                     " and b.create_date<='{start}' and a.{parameterShop} and a.payment_type=4" \
                    .format(start=start,parameterShop=parameterShop)
        cur.execute(sql_before_paid)
        data_before_paid = cur.fetchone()
        data_before_in = data_before_paid['paid'] if data_before_paid['paid'] else 0


        sql_before = " select sum(pay_account) as no_pay" \
                     " from kf_jobs_coupon" \
                     " where DATE_FORMAT(create_date,'%Y-%m-%d')<='{start}' and {parameterShop} and payment_type=4" \
                    .format(start=start,parameterShop=parameterShop)
        cur.execute(sql_before)
        data_before_nopay = cur.fetchone()
        data_before_out = data_before_nopay['no_pay'] if data_before_nopay['no_pay'] else 0

        data_before_total = data_before_out - data_before_in

        sql_out = " select coupon_code,coupon_name,DATE_FORMAT(create_date,'%Y-%m-%d') as create_date," \
                  "shop_code,pay_account,0 as is_pay" \
                  " from kf_jobs_coupon" \
                  " where DATE_FORMAT(create_date,'%Y-%m-%d')>='{start}'" \
                  " and DATE_FORMAT(create_date,'%Y-%m-%d')<='{end}' and {parameterShop} and payment_type=4"\
                  .format(start=start,end=end,parameterShop=parameterShop)
        cur.execute(sql_out)
        data_out = cur.fetchall()

        sql_in = " select a.coupon_code,DATE_FORMAT(a.create_date,'%Y-%m-%d') as create_date," \
                 "a.pay_account,b.shop_code,b.coupon_name,1 as is_pay" \
                 " from kf_jobs_coupon_credit as a,kf_jobs_coupon as b" \
                 " where a.create_date>='{start}' and a.create_date<='{end}' and b.{parameterShop}  and a.coupon_code=b.coupon_code"\
                 .format(start=start,end=end,parameterShop=parameterShop)
        cur.execute(sql_in)
        data_in = cur.fetchall()

        data_io = list(data_in)+list(data_out)
        if len(data_io)>0:
            data_sorted = sorted(data_io,key=itemgetter('create_date'),reverse=False)
            totalPay, MonthNoPay, MonthPay, index, = 0, 0, 0, 0
            resData, monthSubTimeList = [], []
            totalNoPay = float(data_before_total)
            for data in data_sorted:
                time_this = datetime.datetime.strptime(data['create_date'], '%Y-%m-%d')
                if index == 0:
                    time_pre = time_this
                else:
                    time_pre = data_sorted[index - 1]['create_date']
                    time_pre = datetime.datetime.strptime(time_pre, '%Y-%m-%d')
                if isNextMonth(time_this, time_pre):
                    yesterday = datetime.datetime(time_this.year, time_this.month, 1) + datetime.timedelta(days=-1)
                    if yesterday not in monthSubTimeList:
                        monthSubitem = MonthSub(MonthPay, MonthNoPay, yesterday.date())
                        resData.append(monthSubitem)
                        monthSubTimeList.append(yesterday)
                        MonthNoPay = 0
                        MonthPay = 0
                if 'is_pay' in data:
                    if data['is_pay'] == 1:
                        MonthPay += float(data['pay_account'])
                        totalPay += float(data['pay_account'])
                        totalNoPay += -float(data['pay_account'])
                        data['sub'] = totalNoPay
                    else:
                        MonthNoPay += float(data['pay_account'])
                        totalNoPay += float(data['pay_account'])
                        data['sub'] = totalNoPay
                    resData.append(data)

                index += 1

            # 最后一行月度合计
            lastDataTime = resData[len(resData) - 1]['create_date']
            lastDataTime = datetime.datetime.strptime(lastDataTime, '%Y-%m-%d')
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

    return render(request,'report/voucher/payment/month_pay4.html',locals())

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


def MonthSub(MonthPay,MonthNoPay,time):
    item = {}
    item['info'] = '月度合计'
    item['pay'] = MonthPay
    item['noPay'] = MonthNoPay
    item['create_date'] = time
    item['monthSub'] = True
    return item