__author__ = 'admin'
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
from sellcard.common import Method as mth

import datetime,json
from sellcard.models import Orders,OrderPaymentInfo,OrderInfo,OrderPaymentCredit,OrderChangeCard,OrderChangeCardPayment

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
        endStr = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)
        if not end:
            end = today
        buyerName = (mth.getReqVal(request,"buyerName","")).strip()
        #售卡数据
        queryWhereSale1 = " and b.buyer_name='"+buyerName+"'" if buyerName else ''
        queryWhereSale2 = " and b.add_time >='{start}' and b.add_time <='{end}' ".format(start=start, end=endStr)
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sqlSale="select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount, " \
                " IFNULL(c.pay_value, 0) as credit_value, a.pay_id " \
            " from order_payment_info as a ,orders as b " \
            " left join (select sum(p.pay_value) as pay_value, p.order_id from order_payment_credit p group by p.order_id) as c " \
            " on b.order_sn = c.order_id " \
            " where a.order_id=b.order_sn and a.pay_id in (4, 3) and a.is_pay != '1' and b.shop_code ='"+shopcode+"'"+queryWhereSale1+queryWhereSale2
        cur.execute(sqlSale)
        listSale = cur.fetchall()

        cur.close()
        conn.close()

    return render(request, 'card/nopay/ordinary.html', locals())

def detail(request):
    orderSn = request.GET.get('orderSn', '')
    type = request.GET.get('type', '')
    orderPayInfo = []
    order = Orders.objects \
        .values('order_sn', 'shop_code', 'paid_amount', 'disc_amount', 'action_type', 'buyer_name', 'buyer_tel',
                'buyer_company', 'add_time') \
        .filter(order_sn=orderSn)
    orderPayInfo = OrderPaymentInfo.objects.values('pay_id', 'pay_value').filter(order_id=orderSn)
    cardsNum = OrderInfo.objects.filter(order_id=orderSn).count()

    paysDict = {pay['pay_id']: pay['pay_value'] for pay in orderPayInfo}
    if 4 in paysDict.keys():
        orderCredit = OrderPaymentCredit.objects.values('pay_id', 'pay_value').filter(order_id=orderSn)
        totalVal = paysDict[4]
        if orderCredit:
            for item in orderCredit:
                totalVal = float(totalVal) - float(item['pay_value'])
    elif 3 in paysDict.keys():
        totalVal = paysDict[3]
    else:
        totalVal = 0

    return render(request, 'card/nopay/detail.html', locals())


# 更新赊销状态
@transaction.atomic
def save(request):
    shop = request.session.get('s_shopcode', '')
    user_id = request.session.get('s_uid', '')
    uesr_name = request.session.get('s_unameChinese', '')
    orderSn = request.POST.get('orderSn')
    dateStr = request.POST.get('date')
    date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()

    res = {}
    try:
        with transaction.atomic():
            paymentInfo = OrderPaymentInfo.objects.filter(order_id=orderSn)
            if paymentInfo.count():
                payments = paymentInfo.values('pay_id','pay_value')
                paysDict = {pay['pay_id']: pay['pay_value'] for pay in payments}
                if 4 in paysDict.keys():
                    payStr = request.POST.get('payList')
                    payList = json.loads(payStr)
                    paymentInfo.filter(pay_id=4, is_pay=0).update(is_pay=1)
                    for pay in payList:
                        if pay['payId'] == '3':
                            OrderPaymentCredit \
                                .objects \
                                .create(order_id=orderSn, pay_id_old=4,pay_id=pay['payId'],
                                        pay_value=pay['payVal'],remarks=pay['payRmarks'], change_time=date,
                                        bank_name=pay['bankName'], bank_sn=pay['bankSn'],
                                        pay_company=pay['payCompany'], create_time=datetime.datetime.now(),
                                        create_user_id=user_id, create_user_name=uesr_name,shop=shop
                                        )
                        else:
                            OrderPaymentCredit \
                                .objects \
                                .create(order_id=orderSn,pay_id_old=4, pay_id=pay['payId'], pay_value=pay['payVal'],
                                        remarks=pay['payRmarks'], change_time=date, create_time=datetime.datetime.now(),
                                        create_user_id=user_id, create_user_name=uesr_name,shop=shop
                                        )
                elif 3 in paysDict.keys():
                    bankName = request.POST.get('bankName')
                    bankSn = request.POST.get('bankSn')
                    payCompany = request.POST.get('payCompany')
                    remarks = request.POST.get('remarks')

                    pay = paymentInfo.get(pay_id=3, is_pay=0)
                    pay_value = pay.pay_value
                    paymentInfo.filter(pay_id=3, is_pay=0).update(is_pay=1)
                    OrderPaymentCredit \
                        .objects \
                        .create(order_id=orderSn,pay_id_old=3, pay_id=3, pay_value=pay_value,
                                remarks=remarks, change_time=date,
                                bank_name=bankName, bank_sn=bankSn,
                                pay_company=payCompany,create_user_id=user_id, create_user_name=uesr_name,shop=shop
                                )
                res['msg'] = '0'
            else:
                res['msg'] = '1'
    except Exception as e:
        print(e)
        res['msg'] = '1'
    return HttpResponse(json.dumps(res))


