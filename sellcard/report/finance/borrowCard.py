# -*- coding:utf-8 -*-
from django.shortcuts import render
import datetime

from sellcard.common import Method as mth


def index(request):
    role_id = request.session.get('s_roleid')
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    user = request.session.get('s_uid')

    if request.method == 'POST':
        start = request.POST.get('start', '')
        end = request.POST.get('end', '')
        endTime = datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1)
        whereStr = "WHERE t.shopcode = s.shop_code AND t.add_time >='" + start + "' AND t.add_time <='" + str(endTime) + "' "

        if role in ('2', '10'):
            whereStr += " AND t.shopcode ='" + shop + "'"
        conn = mth.getMysqlConn()
        cur = conn.cursor()

        shopsCode = ''
        if role_id == '9':
            shopsCode = mth.getCityShopsCode('T')
            shopsCodeStr = "'" + "','".join(shopsCode) + "'"
            whereStr += " AND t.shopcode IN (" + shopsCodeStr + ")"
        if role_id == '8':
            shopsCode = mth.getCityShopsCode('C')
            shopsCodeStr = "'" + "','".join(shopsCode) + "'"
            whereStr += " AND t.shopcode IN (" + shopsCodeStr + ")"

        sql = """
    SELECT
    	date_format(
    		t.add_time,
    		'%Y年%m月%d日'
    	) AS create_date,
    	s.shop_name,
    	t.order_sn,
    	t.borrow_depart,
    	t.order_val * t.order_num AS borrow_account,
    	IFNULL(o.total_amount, 0) AS balance,
    	IFNULL(o.paid_amount, 0) AS actual,
    	IFNULL(o.discount_rate, 0) AS voucher,
    	t.paid_time
    FROM
    	order_borrow t
    LEFT JOIN orders o ON t.reply_order = o.order_sn,
     shops s """ + whereStr + """
    ORDER BY
    	create_date,
    	s.shop_name
            """
        cur.execute(sql)
        List = cur.fetchall()

        borrow_total = 0.00
        balance_total = 0.00
        actual_total = 0.00
        for row in List:
            borrow_total += float(row['borrow_account'])
            balance_total += float(row['balance'])
            actual_total += float(row['actual'])
    return render(request, 'report/finance/borrowCard.html', locals())
