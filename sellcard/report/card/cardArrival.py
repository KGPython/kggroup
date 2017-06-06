#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.shortcuts import render
import datetime
from sellcard.models import Shops
from sellcard.common import Method as mth

def index(request):
    """
       卡到账列表controllers
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
    sql = u"""
SELECT
	a.shop_code,
	sum(a.pay_value_1) pay_value_1,
	sum(a.pay_value_3) pay_value_3,
	sum(a.pay_value_5) pay_value_5,
	sum(a.pay_value_7) pay_value_7,
	sum(a.pay_value_8) pay_value_8,
	sum(a.pay_value_10) pay_value_10,
	sum(a.pay_value_11) pay_value_11,
	sum(IFNULL(opc6.pay_value, 0)) pay_value_6,
	sum(case when IFNULL(opc4.pay_id, 0) = 1 then
	IFNULL(opc4.pay_value, 0) else 0 end) credit_1,
	sum(case when IFNULL(opc4.pay_id, 0) = 3 then
	IFNULL(opc4.pay_value, 0) else 0 end) credit_3,
	sum(case when IFNULL(opc4.pay_id, 0) = 5 then
	IFNULL(opc4.pay_value, 0) else 0 end) credit_5,
	sum(a.pay_value_total) + sum(IFNULL(opc4.pay_value, 0)) + sum(IFNULL(opc6.pay_value, 0)) total_value
FROM
	(
		SELECT
			ord.order_sn,
			ord.shop_code,
			opi.pay_id,
			CASE
		WHEN opi.pay_id = 1 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_1,
			CASE
		WHEN opi.pay_id = 3 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_3,
			CASE
		WHEN opi.pay_id = 5 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_5,
			CASE
		WHEN opi.pay_id = 7 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_7,
			CASE
		WHEN opi.pay_id = 8 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_8,
			CASE
		WHEN opi.pay_id = 10 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_10,
			CASE
		WHEN opi.pay_id = 11 THEN
			opi.pay_value
		ELSE
			0
		END pay_value_11,
			CASE
		WHEN opi.pay_id not in (4, 6) THEN
			opi.pay_value
		ELSE
			0
		END pay_value_total,
		ord.add_time
	FROM
		orders ord,
		order_payment_info opi
	WHERE
		ord.order_sn = opi.order_id
	AND opi.is_pay = 1
	UNION
		SELECT
			occ.order_sn,
			occ.shop_code,
			occp.pay_id,
			CASE
		WHEN occp.pay_id = 1 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_1,
			CASE
		WHEN occp.pay_id = 3 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_3,
			CASE
		WHEN occp.pay_id = 5 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_5,
			CASE
		WHEN occp.pay_id = 7 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_7,
			CASE
		WHEN occp.pay_id = 8 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_8,
			CASE
		WHEN occp.pay_id = 10 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_10,
			CASE
		WHEN occp.pay_id = 11 THEN
			occp.pay_value
		ELSE
			0
		END pay_value_11,
			CASE
		WHEN occp.pay_id not in (4, 6) THEN
			occp.pay_value
		ELSE
			0
		END pay_value_total,
		occ.add_time
	FROM
		order_change_card occ,
		order_change_card_payment occp
	WHERE
		occ.order_sn = occp.order_id
	AND occp.is_pay = 1
	) a
LEFT JOIN order_payment_credit opc4 ON a.pay_id = 4
AND a.order_sn = opc4.order_id
LEFT JOIN order_payment_credit opc6 ON a.pay_id = 6
AND a.order_sn = opc6.order_id
WHERE a.shop_code IN ({shop})
AND	a.add_time BETWEEN '{start}' AND '{end}'
GROUP BY
	a.shop_code""".format(shop=code_list,
                                            start=start,
                                            end=endTime)
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    cur.execute(sql)
    List = cur.fetchall()
    cur.close()
    conn.close()
    list_len = len(List)

    if list_len > 1:
        total = {}
        total['pay_value_1'] = 0
        total['pay_value_3'] = 0
        total['pay_value_5'] = 0
        total['pay_value_7'] = 0
        total['pay_value_8'] = 0
        total['pay_value_10'] = 0
        total['pay_value_11'] = 0
        total['pay_value_6'] = 0
        total['credit_1'] = 0
        total['credit_3'] = 0
        total['credit_5'] = 0
        total['total_value'] = 0
        for item in List:
            total['pay_value_1'] += item['pay_value_1']
            total['pay_value_3'] += item['pay_value_3']
            total['pay_value_5'] += item['pay_value_5']
            total['pay_value_7'] += item['pay_value_7']
            total['pay_value_8'] += item['pay_value_8']
            total['pay_value_10'] += item['pay_value_10']
            total['pay_value_11'] += item['pay_value_11']
            total['pay_value_6'] += item['pay_value_6']
            total['credit_1'] += item['credit_1']
            total['credit_3'] += item['credit_3']
            total['credit_5'] += item['credit_5']
            total['total_value'] += item['total_value']
    return render(request, 'report/card/cardArrival.html', locals())
