#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json,datetime
from django.db import transaction

from sellcard.models import OrderBorrow,CardInventory,Orders,OrderInfo,OrderPaymentInfo,ActionLog,OrderBorrowInfo
from sellcard.common import Method as mth
from sellcard.common.model import MyError
def index(request):
    shopcode = request.session.get('s_shopcode','')
    operator = request.session.get('s_uid','')
    rates = request.session.get('s_rates')
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    today = str(datetime.date.today())
    start = today
    end = today
    if request.method == 'POST':
        shopcode = request.session.get('s_shopcode','')
        departName = (request.POST.get('departName','')).strip()
        departCode = (request.POST.get('departCode','')).strip()
        state = request.POST.get('state','')
        start = request.POST.get('start','')
        end = request.POST.get('end','')

        nextDay = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)

        kwargs = {}
        whereStr =''
        kwargs.setdefault('operator',operator)
        kwargs.setdefault('is_paid','0')
        whereStr +=' and is_paid="0"'

        if departName:
            whereStr +=' and borrow_depart="'+departName+'"'
            kwargs.setdefault('borrow_depart',departName)
        if departCode:
            whereStr +=' and borrow_depart_code="'+departCode+'"'
            kwargs.setdefault('borrow_depart_code',departCode)
        if start:
            whereStr +=' and add_time>="'+str(start)+'"'
            kwargs.setdefault('add_time__gte',start)
        if end:
            whereStr +=' and add_time<="'+str(nextDay)+'"'
            kwargs.setdefault('add_time__lte',nextDay)

        kwargs.setdefault('shopcode',shopcode)

        #查询借卡明细
        listSale = OrderBorrow\
                .objects\
                .values('order_sn','order_val','order_num','operator','borrow_depart','borrow_depart_code','borrow_phone','borrow_name','add_time','is_paid')\
                .filter(**kwargs).order_by('order_sn')

        totaSale = 0
        listOrderSn = []
        for row in listSale:
            totaSale += row['order_val']
            listOrderSn.append(row['order_sn'])
        #查询退卡明细
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sqlBack = 'select a.order_sn,a.operator,a.borrow_depart,a.borrow_depart_code,SUM(b.card_balance) as back_val,COUNT(b.card_no) as back_num,b.back_time' \
                  ' from order_borrow as a,order_borrow_info as b ' \
                  ' where a.shopcode = "'+shopcode+'" and a.order_sn=b.order_sn and b.is_back="1"'+whereStr+' group by(a.order_sn)'
        # print(sqlBack)
        cur.execute(sqlBack)
        listBack = cur.fetchall()

        totalBack = 0
        for row2 in listBack:
            totalBack += row2['back_val']
        #退卡后应缴费用
        cardOutTotalVal = totaSale-totalBack
        # cardOutTotalVal = 2800

        #查询未退卡明细
        sqlCardNoBack = 'select a.order' \
                        '_sn,b.card_no as cardId,b.card_balance as cardVal from order_borrow as a,order_borrow_info as b ' \
                  ' where a.order_sn=b.order_sn and b.is_back is null '+whereStr+''
        cur.execute(sqlCardNoBack)

        listNoBack = cur.fetchall()
        if len(listNoBack)>0:
            for item in listNoBack:
                item['cardVal'] = str(item['cardVal'])
        else:
            listNoBack=[]

        cur.close()
        conn.close()
    return render(request,'borrowPay.html',locals())

@transaction.atomic
def save(request):
    res = {}

    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    # 检测session中Token值，判断用户提交动作是否合法
    Token = request.session.get('postToken', default=None)
    # 获取用户表单提交的Token值
    userToken = request.POST.get('postToken','')
    if userToken != Token:
        res["msg"] = 0
        return HttpResponse(json.dumps(res))

    actionType = request.POST.get('actionType','')
    #售卡列表
    cardStr = request.POST.get('cardStr','')
    cardList = json.loads(cardStr)

    #借卡单号列表
    orderSnList = request.POST.getlist('orderSnList[]','')


    #赠卡列表
    YcardStr = request.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    Ycash = request.POST.get('Ycash',0.00)
    #支付方式
    payStr = request.POST.get('payStr','')
    payList = json.loads(payStr)
    hjsStr = request.POST.get('hjsStr','')
    #黄金手卡号列表
    hjsList=[]
    if len(hjsStr)>0:
        hjsStr = hjsStr[0:len(hjsStr)-1]
        hjsList = hjsStr.split(',')

    #合计信息
    totalVal = request.POST.get('totalVal',0.00)

    discountRate = request.POST.get('discount',0.00)
    disCode = request.POST.get('disCode','')
    discountVal = request.POST.get('discountVal','')

    Ybalance = request.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
    order_sn = ''
    try:
        with transaction.atomic():
            order_sn = 'S'+mth.setOrderSn()
            for card in cardList:
                orderInfo = OrderInfo()
                orderInfo.order_id = order_sn
                orderInfo.card_id = card['cardId']
                orderInfo.card_balance = float(card['cardVal'])
                orderInfo.card_action = '0'
                orderInfo.card_attr = '1'
                orderInfo.save()

            for Ycard in YcardList:
                YorderInfo = OrderInfo()
                YorderInfo.order_id = order_sn
                YorderInfo.card_id = Ycard['cardId']
                YorderInfo.card_balance = float(Ycard['cardVal'])
                YorderInfo.card_action = '0'
                YorderInfo.card_attr = '2'
                YorderInfo.save()
            for pay in payList:
                orderPay = OrderPaymentInfo()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                if pay['payId']=='4':
                    orderPay.is_pay='0'
                else:
                    orderPay.is_pay='1'
                if pay['payId']=='9':
                    mth.upChangeCode(hjsList,shopcode)

                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                orderPay.save()

            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
            order.total_amount = float(totalVal)+float(discountVal)
            order.paid_amount = float(totalVal)+float(Ybalance)#实付款合计=售卡合计+优惠补差
            order.disc_amount = float(discountVal)#优惠合计
            order.diff_price = Ybalance
            order.shop_code = shopcode
            order.depart = depart
            order.operator_id = operator
            order.action_type = actionType
            order.add_time = datetime.datetime.now()
            order.discount_rate = float(discountRate)/100
            order.order_sn = order_sn
            order.y_cash = Ycash
            order.save()

            #获取所有出卡列表
            cardListTotal = cardList+YcardList
            cardIdList = []
            for card in cardListTotal:
                cardIdList.append(card['cardId'])
            cardsNum = len(cardIdList)

            # 更新kggroup内部卡状态
            resCard = CardInventory.objects.filter(card_no__in=cardIdList).update(card_status='2',card_action='0')
            if resCard != cardsNum:
                raise MyError('系统数据库卡状态更新失败')
            #更新折扣授权码校验码状态
            if disCode:
                resCode = mth.updateDisCode(disCode,shopcode,order_sn)
                if resCode == 0:
                    raise MyError('折扣授权码状态更新失败')

            #更新借卡单的结算状态
            orderSnNum = len(orderSnList)
            resBorrow =  OrderBorrow.objects.filter(order_sn__in=orderSnList).update(is_paid='1',paid_time=datetime.datetime.now())
            if orderSnNum != resBorrow:
                raise MyError('借卡单状态更新失败')

            resBorrow2 = OrderBorrowInfo.objects.filter(card_no__in=cardIdList, is_back=None).update(is_back='0')
            if resBorrow2 != cardsNum-len(YcardList):
                raise MyError('借卡单详情内部数据更新失败')

            # 更新ERP内部卡状态
            resErp = mth.updateCard(cardIdList, '1')
            if resErp != cardsNum:
                mth.updateCard(cardIdList, '9')
                raise MyError('ERP数据库卡状态更新失败')

            res["msg"] = 1
            res["urlRedirect"] ='/kg/sellcard/fornt/cardsale/orderInfo/?orderSn='+order_sn
            ActionLog.objects.create(action='借卡-结算',u_name=request.session.get('s_uname'),cards_out=cardStr+','+YcardStr,add_time=datetime.datetime.now())
            del request.session['postToken']
    except Exception as e:
        res["msg"] = 0
        res["msg_err"] = e
        ActionLog.objects.create(action='借卡-结算',u_name=request.session.get('s_uname'),cards_out=cardStr+','+YcardStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))