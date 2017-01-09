#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.shortcuts import render
import datetime
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
        shops = shops.get(shop_code=shop)
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
