__author__ = 'admin'
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sellcard.common import Method as mth


@csrf_exempt
def index(request):
    operator = str(request.session.get('s_uid',''))
    shopcode = request.session.get('s_shopcode','')
    sql=''
    if request.method == 'POST':
        buyerName = request.POST.get('buyerName','')
        buyerTel = request.POST.get('buyerTel','')
        isPay = request.POST.get('state','')

        queryWhere1= " and b.buyer_name='"+buyerName+"'" if buyerName  else ''
        queryWhere2= " and b.buyer_tel='"+buyerTel+"'" if buyerTel  else ''
        queryWhere3= " and a.is_pay='"+isPay+"'" if isPay  else ''

        sql="select a.pay_value,a.is_pay,a.change_time,b.order_sn,b.user_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
            "from order_payment_info as a ,orders as b " \
            "where b.user_id='"+operator+"'"+queryWhere1+queryWhere2+" and a.order_id=b.order_sn  and a.pay_id=4"+queryWhere3\
            .format(operator=operator)
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        cur.execute(sql)
        list = cur.fetchall()

    return render(request,'nopay.html',locals())