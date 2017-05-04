#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
import datetime

from sellcard.common import Method as mth
from sellcard import views as base
from sellcard.models import Orders,AdminUser,OrderUpCard,OrderChangeCard, OrderInfo, OrderPaymentInfo, OrderUpCardInfo, \
    OrderChangeCardInfo, OrderChangeCardPayment,OrderErr


def index(request):
    role_id = request.session.get('s_roleid')
    s_shop = request.session.get('s_shopcode')
    s_depart = request.session.get('s_depart')
    s_user = request.session.get('s_uid')

    today = str(datetime.date.today())
    shops = []
    users = AdminUser.objects.values('id', 'name').filter(role_id__in=('2', '3','5')).order_by('shop_code')
    if role_id in ('1','6'):
        shops = mth.getCityShopsCode()
    if role_id == '9':
        shops = mth.getCityShopsCode('T')
    if role_id == '8':
        shops = mth.getCityShopsCode('C')
    personList = users.filter(shop_code__in=shops)
    departs = base.findDepart()

    if request.method == 'POST':
        shop,operator,depart = '','',''
        if role_id in ('1','6','8','9'):
            shop = request.POST.get('shop','')
            depart = request.POST.get('depart', '')
            operator = request.POST.get('operator', '')
        elif  role_id in ('2','10') :
            shop = s_shop
            depart = request.POST.get( 'depart', '')
            operator = request.POST.get('operator', '')
        elif role_id in ('3','5'):
            shop = s_shop
            depart = s_depart
            operator = s_user
        actionType = request.POST.get('actionType','1')
        start = request.POST.get('start',today)
        end = request.POST.get('end',today)
        endTime = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(1)
        page = request.POST.get('page',1)

        kwargs = {}
        if shop:
            kwargs.setdefault('shop_code',shop)
        if operator:
            kwargs.setdefault('operator_id',operator)
        if depart:
            kwargs.setdefault('depart',depart)
        kwargs.setdefault('add_time__gte',start)
        kwargs.setdefault('add_time__lte',endTime)

        resList, paidTotal, discTotal, cardCount = getData(actionType,kwargs)
        paginator = Paginator(resList,20)
        try:
            resList = paginator.page(page)
            page_next = mth.getNextPageNum(resList)
            page_prev = mth.getPrevPageNum(resList)

        except Exception as e:
            print(e)
    return render(request, 'report/card/saleGroupByOrder/index.html', locals())


def getData(actionType,kwargs):
    resList = []
    paidTotal = 0.00
    discTotal = 0.00
    cardCount = 0
    if actionType=='1':
        resList = Orders.objects.values('shop_code','depart','operator_id','order_sn','action_type','paid_amount','disc_amount','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id','add_time')
        for item in resList:
            paidTotal += float(item['paid_amount'])
            discTotal += float(item['disc_amount'])
            cardCount +=1
    elif actionType=='2':
        resList = OrderUpCard.objects.values('shop_code','depart','operator_id','order_sn','diff_price','user_name','user_phone','modified_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id','modified_time')
    elif actionType=='3':
        resList = OrderChangeCard.objects.values('shop_code','depart','operator_id','order_sn','total_in_price','total_out_price','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id','add_time')
    return resList,paidTotal,discTotal,cardCount


def orderDetail(request):
    role = request.session.get('s_roleid')
    orderSn = request.GET.get('orderSn', '')
    actionType = request.GET.get('actionType', '1')
    total_in_price = total_out_price = 0.00
    payments = base.findPays()

    if actionType == '1':
        order = Orders.objects \
            .values('order_sn', 'shop_code', 'paid_amount', 'disc_amount', 'action_type', 'buyer_name', 'buyer_tel',
                    'buyer_company', 'add_time', 'remark') \
            .filter(order_sn=orderSn)
        orderInfo = OrderInfo.objects.values('card_id', 'card_balance').filter(order_id=orderSn)
        orderPayInfo = OrderPaymentInfo.objects.values('pay_id', 'pay_value', 'remarks').filter(order_id=orderSn)
        cardsNum = OrderInfo.objects.filter(order_id=orderSn).count()
    elif actionType == '2':
        order = OrderUpCard.objects \
            .values('order_sn', 'shop_code', 'action_type', 'total_amount', 'total_price', 'fill_amount', 'fill_price',
                    'diff_price', 'state', 'user_name', 'user_phone') \
            .filter(order_sn=orderSn)
        # 丢失卡
        orderInfo = OrderUpCardInfo.objects.values('card_no', 'card_value', 'card_balance', 'card_attr').filter(order_sn=orderSn)
        cardsNum = OrderUpCardInfo.objects.filter(order_sn=orderSn).count()
    elif actionType == '3':
        order = OrderChangeCard.objects \
            .values('shop_code', 'depart', 'operator_id', 'order_sn', 'total_in_price', 'total_in_amount',
                    'total_out_price', 'total_out_amount', 'add_time') \
            .filter(order_sn=orderSn)
        orderInfo = OrderChangeCardInfo.objects.values('card_no', 'card_attr', 'card_value', 'card_balance') \
            .filter(order_sn=orderSn)
        cardsNum = OrderChangeCardInfo.objects.values('card_attr', 'card_no', 'card_value', 'card_balance') \
            .filter(order_sn=orderSn)

        # 比较进卡金额与出卡金额，如果出卡金额 > 金卡金额，则认为是补差价购卡
        for d in order:
            total_in_price = d['total_in_price']
            total_out_price = d['total_out_price']

        if total_out_price > total_in_price:
            # 获取补差购卡支付方式、金额、是否支付（赊销、汇款）
            orderPayment = OrderChangeCardPayment.objects.values('pay_id', 'pay_value', 'is_pay')\
                .filter(order_id=orderSn)

        cardsInNum = 0
        cardsOutNum = 0
        for num in cardsNum:
            if num['card_attr'] == '1':
                cardsInNum += 1
            if num['card_attr'] == '0':
                cardsOutNum += 1
    if order:
        shop = order[0]['shop_code']
    return render(request, 'report/card/saleGroupByOrder/orderDetail.html', locals())



