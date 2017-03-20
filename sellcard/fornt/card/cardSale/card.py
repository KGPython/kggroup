# -*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders, OrderInfo, OrderPaymentInfo, CardInventory, ActionLog, PrintExplain,Payment
from django.http import HttpResponse
import json,datetime
from django.db import transaction
from django.db.models import Sum,Count

from sellcard.common import Method as mth
from sellcard.common.model import MyError



def index(request):
    operator = request.session.get('s_uid','')
    roleid= request.session.get("s_roleid",'')
    rates = request.session.get('s_rates')
    disc_level = request.session.get('disc_level')
    shopcode = request.session.get('s_shopcode','')

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    return render(request, 'card/sale/cardSale.html', locals())


@transaction.atomic
def saveOrder(request):
    path = request.path
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    actionType = request.POST.get('actionType','')
    #售卡列表
    cardStr = request.POST.get('cardStr','')
    cardList = json.loads(cardStr)
    #赠卡列表
    YcardStr = request.POST.get('YcardStr','')
    YcardList = json.loads(YcardStr)
    Ycash = request.POST.get('Ycash','')
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

    discountRate = float(request.POST.get('discount',0.00))/100
    disCode = request.POST.get('disCode','')
    discountVal = float(request.POST.get('discountVal',''))

    Ybalance = request.POST.get('Ybalance',0.00)

    #买卡人信息
    buyerName = request.POST.get('buyerName','')
    buyerPhone = request.POST.get('buyerPhone','')
    buyerCompany = request.POST.get('buyerCompany','')
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

            isThird = False
            #保存OrderPaymentInfo
            payDiscDict = mth.getPayDiscDict()
            oderPaymentList = []
            for pay in payList:
                orderPay = OrderPaymentInfo()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                #处理混合支付的优惠
                is_pay = 1
                if pay['payId'] in ('3','4'):
                    is_pay = '0'
                elif pay['payId'] == '6':
                    isThird = True
                    is_pay = '0'
                    discountRate = payDiscDict[pay['payId']]
                    discountVal = Ycash = float(pay['payVal']) * float(discountRate)
                elif pay['payId'] in ('7','8','10','11'):
                    isThird = True
                    discountRate = payDiscDict[pay['payId']]
                    discountVal = Ycash = float(pay['payVal']) * float(discountRate)

                if pay['payId'] == '9':
                    isThird = True
                    mth.upChangeCode(hjsList,shopcode)

                orderPay.is_pay = is_pay
                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                oderPaymentList.append(orderPay)
            OrderPaymentInfo.objects.bulk_create(oderPaymentList)

            # 保存OrderInfo
            orderInfoList = []
            for card in cardList:
                orderInfo = OrderInfo()
                orderInfo.order_id = order_sn
                orderInfo.card_id = card['cardId'].strip()
                orderInfo.card_balance = float(card['cardVal'])
                orderInfo.card_action = '0'
                orderInfo.card_attr = '1'
                orderInfoList.append(orderInfo)
            if not isThird:
                for Ycard in YcardList:
                    YorderInfo = OrderInfo()
                    YorderInfo.order_id = order_sn
                    YorderInfo.card_id = Ycard['cardId'].strip()
                    YorderInfo.card_balance = float(Ycard['cardVal'])
                    YorderInfo.card_action = '0'
                    YorderInfo.card_attr = '2'
                    orderInfoList.append(YorderInfo)
            OrderInfo.objects.bulk_create(orderInfoList)

            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
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

            #获取所有出卡列表
            cardListTotal = cardList+YcardList
            cardIdList = []
            for card in cardListTotal:
                cardIdList.append(card['cardId'])
            cardsNum = len(cardIdList)

            # 更新kggroup内部卡状态
            resCard = CardInventory.objects.filter(card_no__in=cardIdList,card_status='1',is_store='0')\
                .update(card_status='2',card_action='0')
            if resCard != cardsNum:
                raise MyError('CardInventory状态更新失败')
            #更新折扣授权码校验码状态
            if disCode:
                resCode = mth.updateDisCode(disCode,shopcode,order_sn)
                if resCode == 0:
                    raise MyError('折扣授权码状态更新失败')

            # 更新Guest
            updateConfList = []
            updateConfList.append({'ids': cardIdList, 'mode': '1', 'count': cardsNum})
            resGuest = mth.updateCard(updateConfList)
            if resGuest['status'] == 0:
                raise MyError(resGuest['msg'])

            res["status"] = 1
            res["urlRedirect"] ='/kg/sellcard/fornt/cardsale/orderInfo/?orderSn='+order_sn
            ActionLog.objects.create(url=path,u_name=request.session.get('s_uname'),cards_out=json.dumps(cardIdList),add_time=datetime.datetime.now())
            del request.session['postToken']
    except Exception as e:
        if hasattr(e,'value'):
            res['msg'] = e.value
        res["status"] = 0
        ActionLog.objects.create(url=path,u_name=request.session.get('s_uname'),add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))


def info(request):
    orderSn = request.GET.get('orderSn','').strip()
    today = datetime.date.today()

    order = Orders.objects\
            .values('shop_code','operator_id','paid_amount','disc_amount','diff_price','y_cash','buyer_name','add_time')\
            .filter(order_sn=orderSn)
    infoList = OrderInfo.objects.values('card_balance','card_attr').filter(order_id=orderSn).annotate(subVal=Sum('card_balance'),subNum=Count('card_id'))

    totalNum = 0
    if len(infoList):
        for info in infoList:
            totalNum += int(info['subNum'])
        return render(request, 'common/orderInfo.html', locals())
    else:
        res={}
        res['msg']='此订单不存在'
        return render(request, '500.html', locals())


def reprint(request):
    '''
    订单重打印
    :param request:
    :return:
    '''
    # 初始化
    num = 0
    res = {}

    orderSn = request.GET.get('orderSn', '').strip()
    order = Orders.objects.values('print_num').filter(order_sn=orderSn)

    for o in order:
        if o['print_num'] is None:
            num = 0
        else:
            num = o['print_num']

    res['num'] = num
    # 记录打印次数
    Orders.objects.filter(order_sn=orderSn).update(print_num=num + 1)

    return HttpResponse(json.dumps(res))


def print_explain(request):
    res = {}
    orderSn = request.GET.get('orderSn', '').strip()
    reMark = request.GET.get('remark', '').strip()

    order = PrintExplain.objects.create(order_sn=orderSn, remark=reMark)

    if order:
        res['success'] = 'True'
    else:
        res['success'] = 'False'

    return HttpResponse(json.dumps(res))