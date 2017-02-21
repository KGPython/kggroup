__author__ = 'admin'
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from sellcard.common import Method as mth

import datetime,json
from sellcard.models import Orders,OrderPaymentInfo,OrderInfo,OrderChangeCard,OrderChangeCardPayment

def index(request):
    if request.method == 'POST':
        operator = str(request.session.get('s_uid', ''))
        shopcode = request.session.get('s_shopcode', '')

        today = datetime.datetime.today().replace(hour=23,minute=59,second=59)
        monthFirstDay = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        start = request.POST.get('start')
        if not start:
            start = monthFirstDay
        end = request.POST.get('end')
        if not end:
            end = today
        buyerName = (mth.getReqVal(request,"buyerName","")).strip()
        #售卡数据
        queryWhereSale1 = " and b.buyer_name='"+buyerName+"'" if buyerName else ''
        queryWhereSale2 = " and b.add_time >='{start}' and b.add_time <='{end}' ".format(start=start, end=end)
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sqlSale="select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
            "from order_payment_info as a ,orders as b " \
            "where a.order_id=b.order_sn and a.pay_id=4 and a.is_pay='0' and b.shop_code ='"+shopcode+"'"+queryWhereSale1+queryWhereSale2
        cur.execute(sqlSale)
        listSale = cur.fetchall()

        cur.close()
        conn.close()

    return render(request, 'card/nopay/ordinary.html', locals())

def detail(request):
    orderSn = request.GET.get('orderSn', '')
    type = request.GET.get('type', '')
    orderPayInfo = []
    if type == 'sale':
        order = Orders.objects \
            .values('order_sn', 'shop_code', 'paid_amount', 'disc_amount', 'action_type', 'buyer_name', 'buyer_tel',
                    'buyer_company', 'add_time') \
            .filter(order_sn=orderSn)
        orderPayInfo = OrderPaymentInfo.objects.values('pay_id', 'pay_value').filter(order_id=orderSn)
        cardsNum = OrderInfo.objects.filter(order_id=orderSn).count()

    paysDict = {pay['pay_id']: pay['pay_value'] for pay in orderPayInfo}
    if 4 in paysDict.keys():
        totalVal = paysDict[4]
    else:
        totalVal = 0

    return render(request, 'card/nopay/detail.html', locals())


# 更新赊销状态
@transaction.atomic
def save(request):
    orderSn = request.POST.get('orderSn')
    dateStr = request.POST.get('date')
    date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
    payStr = request.POST.get('payList')
    payList = json.loads(payStr)
    res = {}
    try:
        with transaction.atomic():
            paymentInfo = OrderPaymentInfo.objects.filter(order_id=orderSn)
            paymentInfo.filter(order_id=orderSn, pay_id=4,is_pay=0).delete()
            for pay in payList:
                if pay['payId'] == '3':
                    OrderPaymentInfo \
                        .objects \
                        .create(order_id=orderSn, pay_id=pay['payId'], pay_value=pay['payVal'],
                                remarks=pay['payRmarks'], is_pay=1, change_time=date,
                                bank_name=pay['bankName'], bank_sn=pay['bankSn'],
                                pay_company=pay['payCompany']
                                )
                else:
                    OrderPaymentInfo \
                        .objects \
                        .create(order_id=orderSn, pay_id=pay['payId'], pay_value=pay['payVal'],
                                remarks=pay['payRmarks'], is_pay=1, change_time=date
                                )
            res['msg'] = '0'
    except Exception as e:
        print(e)
        res['msg'] = '1'
    return HttpResponse(json.dumps(res))


