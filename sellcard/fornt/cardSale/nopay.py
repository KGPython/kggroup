__author__ = 'admin'
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sellcard.common import Method as mth
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo


@csrf_exempt
def index(request):
    operator = str(request.session.get('s_uid',''))
    shopcode = request.session.get('s_shopcode','')
    sql=''
    if request.method == 'POST':
        buyerName = mth.getReqVal(request,"buyerName","")
        buyerTel = mth.getReqVal(request,"buyerTel","")
        isPay = mth.getReqVal(request,"state","")

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
        cur.close()
        conn.close()

    return render(request,'nopay.html',locals())

def detail(request):
    orderSn = request.GET.get('ordersn','')
    order = Orders.objects\
            .values('order_sn','shop_code','paid_amount','disc_amount','buyer_name','buyer_tel','buyer_company','add_time')\
            .filter(order_sn=orderSn)

    orderInfo = OrderInfo.objects.values('card_id','card_balance').filter(order_id=orderSn)
    orderPayInfo = OrderPaymentInfo.objects.values('pay_id','pay_value','remarks').filter(order_id=orderSn)
    cardsNum = OrderInfo.objects.filter(order_id=orderSn).count()
    return render(request,'nopayDetail.html',locals())