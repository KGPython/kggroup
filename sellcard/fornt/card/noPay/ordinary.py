__author__ = 'admin'
from django.shortcuts import render
from sellcard.common import Method as mth
from datetime import datetime

def index(request):

    if request.method == 'POST':
        operator = str(request.session.get('s_uid', ''))
        shopcode = request.session.get('s_shopcode', '')

        today = datetime.today().replace(hour=23,minute=59,second=59)
        monthFirstDay = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        start = request.POST.get('start')
        if not start:
            start = monthFirstDay
        end = request.POST.get('end')
        if not end:
            end = today
        buyerName = (mth.getReqVal(request,"buyerName","")).strip()
        isPay = mth.getReqVal(request,"state","")

        queryWhere1 = " and b.buyer_name='"+buyerName+"'" if buyerName else ''
        queryWhere2 = " and a.is_pay='"+isPay+"'" if isPay else ''
        queryWhere3 = " and b.add_time >='{start}' and b.add_time <='{end}' "\
                      .format(start=start, end=end)

        sql="select a.pay_value,a.is_pay,a.change_time,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
            "from order_payment_info as a ,orders as b " \
            "where b.operator_id='"+operator+"'"+queryWhere1+queryWhere3+" and a.order_id=b.order_sn  and a.pay_id=4"+queryWhere2
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        cur.execute(sql)
        list = cur.fetchall()
        cur.close()
        conn.close()

    return render(request, 'card/nopay/ordinary.html', locals())


