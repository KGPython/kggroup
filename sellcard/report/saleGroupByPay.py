#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import datetime

from sellcard.common import Method as mth
@csrf_exempt
def index(request):
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    user = request.session.get('s_uid')

    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')
        endTime = datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1)
        whereStr ="WHERE a.add_time >='"+start+"' AND a.add_time <='"+str(endTime)+"' AND a.order_sn = b.order_id "

        if role == '2':
            whereStr += " AND a.shop_code ='"+shop+"'"
        conn = mth.getMysqlConn()
        cur = conn.cursor()

        sql = "SELECT b.pay_id,SUM(b.pay_value) AS pay_value FROM orders as a,order_payment_info as b "+whereStr+"GROUP BY b.pay_id ORDER BY b.pay_id"
        cur.execute(sql)
        payList = cur.fetchall()

        nopay = "SELECT SUM(b.pay_value) AS pay_value FROM orders as a,order_payment_info as b " \
                "WHERE a.add_time >='"+start+"' AND a.add_time <='"+str(endTime)+"' AND a.order_sn = b.order_id AND b.is_pay='0' AND b.pay_id=4"

        cur.execute(nopay)
        nopayDict = cur.fetchone()

        payTotal = 0.00
        for row in payList:
            payTotal += float(row['pay_value'])
    return render(request, 'report/saleGroupByPay.html', locals())
