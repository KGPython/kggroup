#__author__ = 'admin'
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from sellcard.common import Method as mth

import datetime,json
from sellcard.models import OrderPaymentInfo,OrderChangeCardPayment,OrderPaymentCredit

def index(request):
    # if request.method == 'POST':
    #     today = datetime.datetime.now()
    #     monthFirstDay = datetime.datetime.today().replace(day=1)
    #     shop = request.session.get('s_shopcode', '')
    #     start = request.POST.get('start', monthFirstDay)
    #     end = request.POST.get('end', today)
    #     order_sn = request.POST.get('order_sn', '')
    #
    #     conn = mth.getMysqlConn()
    #     cur = conn.cursor()
    #     queryWhere1 = " and b.add_time >='{start} 00:00:00'  and b.add_time <='{end} 23:59:59' ".format(start=start,
    #                                                                                                     end=end)
    #
    #     if order_sn != '':
    #         queryWhere1 += " and b.order_sn like '%{order_sn}%'".format(order_sn=order_sn)
    #     # 售卡数据
    #     sqlSale = "select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.buyer_name,b.buyer_tel,b.paid_amount " \
    #               "from order_payment_info as a ,orders as b " \
    #               "where b.shop_code='" + shop + "'" + queryWhere1 + " and a.order_id=b.order_sn  and a.pay_id=6 and a.is_pay='0' "
    #
    #     cur.execute(sqlSale)
    #     listSale = cur.fetchall()
    #
    #     # 换卡数据
    #     sqlChange = "select a.pay_value,b.order_sn,b.operator_id,b.add_time,b.user_name as buyer_name," \
    #                 "b.user_phone as buyer_tel,(b.total_out_price-b.total_in_price) as paid_amount " \
    #                 "from order_change_card_payment as a ,order_change_card as b " \
    #                 "where b.shop_code='" + shop + "'" + queryWhere1 + " and a.order_id=b.order_sn  and a.pay_id=6 and a.is_pay='0' "
    #     cur.execute(sqlChange)
    #     listChange = cur.fetchall()
    #
    #     cur.close()
    #     conn.close()
    #     totalVal = 0
    #     if (isinstance(listSale, tuple)):
    #         listSale = list(listSale)
    #     if (isinstance(listChange, tuple)):
    #         listChange = list(listChange)
    #     listYD = listSale + listChange
    #     for YD in listYD:
    #         totalVal += YD['pay_value']
    return render(request, 'card/nopay/yidong.html', locals())


@transaction.atomic
def save(request):
    dateStr = request.POST.get('date')
    u_id = request.session.get('s_uid', '')
    u_name = request.session.get('s_unameChinese', '')
    shop = request.session.get('s_shopcode', '')
    date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
    pay_value = request.POST.get('pay_value')
    orderSn = 'YD'+mth.createSnCreditYD()
    res = {}
    try:
        OrderPaymentCredit \
        .objects \
        .create(order_id=orderSn, pay_id_old=6, pay_id=3, pay_value=pay_value, change_time=date,
                create_time=datetime.datetime.now(),create_user_id=u_id, create_user_name=u_name,shop=shop)
        res['msg'] = 0
    except :
        res['msg'] = 1
    return HttpResponse(json.dumps(res))
