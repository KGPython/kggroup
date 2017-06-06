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
	sum(a.pay_value) pay_value_3,
	sum(IFNULL(opc4.pay_value, 0)) pay_value_4,
	sum(IFNULL(opc6.pay_value, 0)) pay_value_6,
	sum(a.pay_value) + sum(IFNULL(opc4.pay_value, 0)) + sum(IFNULL(opc6.pay_value, 0)) total_value
FROM
	(
		SELECT
			ord.order_sn,
			ord.shop_code,
			opi.pay_id,
			CASE
		WHEN opi.pay_id = 3 THEN
			opi.pay_value
		ELSE
			0
		END pay_value,
		ord.add_time
	FROM
		orders ord,
		order_payment_info opi
	WHERE
		ord.order_sn = opi.order_id
	AND opi.is_pay = 1
	AND opi.pay_id IN (3, 4, 6)
	UNION
		SELECT
			occ.order_sn,
			occ.shop_code,
			occp.pay_id,
			CASE
		WHEN occp.pay_id = 3 THEN
			occp.pay_value
		ELSE
			0
		END pay_value,
		occ.add_time
	FROM
		order_change_card occ,
		order_change_card_payment occp
	WHERE
		occ.order_sn = occp.order_id
	AND occp.is_pay = 1
	AND occp.pay_id IN (3, 4, 6)
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
        total['pay_value_3'] = 0
        total['pay_value_4'] = 0
        total['pay_value_6'] = 0
        total['total_value'] = 0
        for item in List:
            total['pay_value_3'] += item['pay_value_3']
            total['pay_value_4'] += item['pay_value_4']
            total['pay_value_6'] += item['pay_value_6']
            total['total_value'] += item['total_value']
    return render(request, 'report/card/cardArrival.html', locals())
