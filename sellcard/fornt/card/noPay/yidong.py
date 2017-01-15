__author__ = 'admin'
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from sellcard.common import Method as mth

import datetime,json
from sellcard.models import OrderPaymentInfo,OrderChangeCardPayment

def index(request):
    if request.method == 'POST':
        today = datetime.datetime.now()
        monthFirstDay = datetime.datetime.today().replace(day=1)
        shop = request.session.get('s_shopcode','')
        start = request.POST.get('start',monthFirstDay)
        end   = request.POST.get('end',today)

        conn = mth.getMysqlConn()
        cur = conn.cursor()
        queryWhere1 = " and b.add_time >='{start} 00:00:00'  and b.add_time <='{end} 23:59:59' ".format(start=start,end=end)
        #售卡数据
        sqlSale = "select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
              "from order_payment_info as a ,orders as b " \
              "where b.shop_code='" + shop + "'" + queryWhere1 + " and a.order_id=b.order_sn  and a.pay_id=6 and a.is_pay='0' "

        cur.execute(sqlSale)
        listSale = cur.fetchall()

        # 换卡数据
        sqlChange = "select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.user_name as buyer_name," \
                    "b.user_phone as buyer_tel,(b.total_out_price-b.total_in_price) as paid_amount " \
                    "from order_change_card_payment as a ,order_change_card as b " \
                    "where b.shop_code='" + shop + "'" + queryWhere1 + " and a.order_id=b.order_sn  and a.pay_id=6 and a.is_pay='0' "
        cur.execute(sqlChange)
        listChange = cur.fetchall()

        cur.close()
        conn.close()
        totalVal = 0
        if(isinstance(listSale,tuple)):
            listSale = list(listSale)
        if (isinstance(listChange, tuple)):
            listChange = list(listChange)
        listYD = listSale+listChange
        for YD in listYD:
            totalVal += YD['pay_value']


    return render(request, 'card/nopay/yidong.html', locals())


@transaction.atomic
def save(request):
    dateStr = request.POST.get('date')
    date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
    orderSnListStr = request.POST.get('orderSnList')
    orderSnList = orderSnListStr.split(',')
    res = {}
    try:
        with transaction.atomic():
            for orderSn in orderSnList:
                if orderSn.find('S')==0:
                    OrderPaymentInfo.objects.filter(order_id=orderSn,pay_id=6,is_pay=0).update(pay_id=3,change_time=date,is_pay=1)
                elif orderSn.find('C')==0:
                    OrderChangeCardPayment.objects.filter(order_id=orderSn,pay_id=6,is_pay=0).update(pay_id=3,change_time=date,is_pay=1)
            res['msg'] = '0'
    except Exception as e:
        print(e)
        res['msg'] = '1'
    return HttpResponse(json.dumps(res))


