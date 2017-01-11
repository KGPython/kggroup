__author__ = 'admin'
from django.shortcuts import render
from sellcard.common import Method as mth
from datetime import datetime

def index(request):
    if request.method == 'POST':
        today = datetime.now()
        monthFirstDay = datetime.today().replace(day=1)
        shop = request.session.get('s_shopcode','')
        start = request.POST.get('start',monthFirstDay)
        end   = request.POST.get('end',today)
        isPay = mth.getReqVal(request, "state", '')

        queryWhere1 = " and b.add_time >='{start} 00:00:00'  and b.add_time <='{end} 23:59:59' ".format(start=start,end=end)
        queryWhere3 = " and a.is_pay='" + isPay + "'" if isPay else ''

        sql = "select a.pay_value,a.is_pay,a.change_time,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
              "from order_payment_info as a ,orders as b " \
              "where b.shop_code='" + shop + "'" + queryWhere1 + " and a.order_id=b.order_sn  and a.pay_id=6" + queryWhere3
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        cur.execute(sql)
        list = cur.fetchall()
        cur.close()
        conn.close()

    return render(request, 'card/nopay/yidong.html', locals())


