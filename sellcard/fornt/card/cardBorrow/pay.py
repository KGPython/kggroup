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

        #查询退卡明细
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sqlBack = 'select a.order_sn,a.operator,a.borrow_depart,a.borrow_depart_code,SUM(b.card_balance) as back_val,COUNT(b.card_no) as back_num,b.back_time' \
                  ' from order_borrow as a,order_borrow_info as b ' \
                  ' where a.shopcode = "'+shopcode+'" and a.order_sn=b.order_sn and b.is_back="1"'+whereStr+' group by(a.order_sn)'
        cur.execute(sqlBack)
        listBack = cur.fetchall()


        #查询未退卡明细
        sqlCardNoBack = 'select a.order' \
                        '_sn,b.card_no as cardId,b.card_balance as cardVal from order_borrow as a,order_borrow_info as b ' \
                  ' where a.shopcode ="'+shopcode+'" and a.order_sn=b.order_sn and b.is_back is null '+whereStr+''
        cur.execute(sqlCardNoBack)

        listNoBack = cur.fetchall()
        if len(listNoBack)>0:
            for item in listNoBack:
                item['cardVal'] = str(item['cardVal'])
        else:
            listNoBack=[]

        cur.close()
        conn.close()
    return render(request, 'card/borrow/pay.html', locals())

@transaction.atomic
def save(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')
    actionType = request.POST.get('actionType','')

    #借卡单号列表
    orderSnList = request.POST.get('orderSnList[]','')
    orderBorrow = OrderBorrow.objects.filter(order_sn=orderSnList)
    if not orderBorrow.count():
        return {'status':0,'msg':'此订单不存在'}
    buyer = orderBorrow.values('borrow_name', 'borrow_depart', 'borrow_phone').first()

    #未退还卡列表
    cardList = OrderBorrowInfo.objects.values('card_no','card_balance').filter(order_sn=orderSnList,is_back=None)
    #赠卡列表
    YcardStr = request.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    Ycash = request.POST.get('Ycash',0.00)

    #支付方式
    payStr = request.POST.get('payStr','')
    payList = json.loads(payStr)

    # 黄金手卡号列表
    # hjsStr = request.POST.get('hjsStr','')
    # hjsList=[]
    # if len(hjsStr)>0:
    #     hjsStr = hjsStr[0:len(hjsStr)-1]
    #     hjsList = hjsStr.split(',')

    #合计信息
    totalVal = request.POST.get('totalVal',0.00)
    discountRate = float(request.POST.get('discount',0.00))/100
    disCode = request.POST.get('disCode','')
    discountVal = float(request.POST.get('discountVal',''))
    Ybalance = request.POST.get('Ybalance',0.00)

    order_sn = ''
    res = {}
    try:
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            raise MyError('表单重复提交，刷新页面后，重试！')

        with transaction.atomic():
            order_sn = 'S'+mth.setOrderSn()

            payDiscDict = mth.getPayDiscDict()
            isThird = False
            paymentList = []
            for pay in payList:
                orderPay = OrderPaymentInfo()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                # 处理混合支付的优惠
                is_pay = 1
                if pay['payId'] =='3':
                    is_pay = '0'
                elif pay['payId'] =='4':
                    is_pay = '0'
                    orderPay.received_time = pay['received_time']
                elif pay['payId'] == '6':
                    isThird = True
                    is_pay = '0'
                    discountRate = payDiscDict[pay['payId']]
                    discountVal = Ycash = float(pay['payVal']) * float(discountRate)
                elif pay['payId'] in ('7', '8', '10', '11'):
                    isThird = True
                    discountRate = payDiscDict[pay['payId']]
                    discountVal = Ycash = float(pay['payVal']) * float(discountRate)
                orderPay.is_pay = is_pay

                # if pay['payId']=='9':
                #     isThird = True
                #     mth.upChangeCode(hjsList,shopcode)

                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                paymentList.append(orderPay)
            OrderPaymentInfo.objects.bulk_create(paymentList)

            infoList = []
            for card in cardList:
                orderInfo = OrderInfo()
                orderInfo.order_id = order_sn
                orderInfo.card_id = card['card_no']
                orderInfo.card_balance = float(card['card_balance'])
                orderInfo.card_action = '0'
                orderInfo.card_attr = '1'
                infoList.append(orderInfo)
            if not isThird:
                for Ycard in YcardList:
                    YorderInfo = OrderInfo()
                    YorderInfo.order_id = order_sn
                    YorderInfo.card_id = Ycard['cardId']
                    YorderInfo.card_balance = float(Ycard['cardVal'])
                    YorderInfo.card_action = '0'
                    YorderInfo.card_attr = '2'
                    infoList.append(YorderInfo)
            OrderInfo.objects.bulk_create(infoList)

            order = Orders()
            order.buyer_name = buyer['borrow_name']
            order.buyer_tel = buyer['borrow_phone']
            order.buyer_company = buyer['borrow_depart']
            order.total_amount = float(totalVal)+float(discountVal)
            order.paid_amount = float(totalVal)+float(Ybalance)#实付款合计=售卡合计+优惠补差
            order.disc_amount = discountVal#优惠合计
            order.diff_price = Ybalance
            order.shop_code = shopcode
            order.depart = depart
            order.operator_id = operator
            order.action_type = actionType
            order.add_time = datetime.datetime.now()
            order.discount_rate = discountRate
            order.order_sn = order_sn
            order.y_cash = Ycash
            order.save()


            #未退回卡列表 chedan
            cardIdBorrowList = [card['card_no'] for card in cardList]
            #优惠卡列表
            cardIdDisclist = [card['cardId'] for card in YcardList]


            # 更新kggroup内部优惠赠送卡状态
            resCard = CardInventory.objects.filter(card_no__in=cardIdDisclist,card_status='1',is_store='0')\
                .update(card_status='2',card_action='0')
            if resCard != len(cardIdDisclist):
                raise MyError('CardInventory状态更新失败')

            #更新折扣授权码校验码状态
            if disCode:
                resCode = mth.updateDisCode(disCode,shopcode,order_sn)
                if resCode == 0:
                    raise MyError('折扣授权码状态更新失败')

            #更新借卡单的结算状态
            resBorrow =  orderBorrow.update(is_paid='1',paid_time=datetime.datetime.now(),reply_order=order_sn)
            if not resBorrow:
                raise MyError('OrderBorrow状态更新失败')

            resBorrow2 = OrderBorrowInfo.objects.filter(order_sn=orderSnList,card_no__in=cardIdBorrowList, is_back=None).update(is_back='0')
            if resBorrow2 != len(cardIdBorrowList):
                raise MyError('OrderBorrowInfo数据更新失败')

            # 更新ERP内部优惠赠送卡状态
            if len(cardIdDisclist)>0:
                # 更新Guest
                updateConfList = []
                updateConfList.append({'ids': cardIdDisclist, 'mode': '1', 'count': len(cardIdDisclist)})
                resGuest = mth.updateCard(updateConfList)
                if resGuest['status'] == 0:
                    raise MyError(resGuest['msg'])

            res["status"] = 1
            res["urlRedirect"] ='/kg/sellcard/fornt/cardsale/orderInfo/?orderSn='+order_sn
            cardOutTotal = cardIdBorrowList + cardIdDisclist
            ActionLog.objects.create(action='借卡-结算',u_name=request.session.get('s_uname'),cards_out=json.dumps(cardOutTotal),add_time=datetime.datetime.now())
            del request.session['postToken']
    except Exception as e:
        res["status"] = 0
        if hasattr(e,'value'):
            res['msg'] = e.value
        ActionLog.objects.create(action='借卡-结算',u_name=request.session.get('s_uname'),add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))