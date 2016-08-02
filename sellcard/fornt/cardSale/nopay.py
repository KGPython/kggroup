__author__ = 'admin'
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sellcard.common import Method as mth

def index(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')

    sql="select a.pay_value,b.order_sn,b.user_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
        "from order_payment_info as a ,orders as b " \
        "where b.user_id='"+str(operator)+"' and a.order_id=b.order_sn and is_pay='0'"
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    cur.execute(sql)
    list = cur.fetchall()

    return render(request,'nopay.html',locals())