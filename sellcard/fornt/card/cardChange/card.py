#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
from sellcard.models import CardInventory, OrderChangeCard, OrderChangeCardInfo,ActionLog, OrderChangeCardPayment
from django.db.models import F
from django.http import HttpResponse
import json
import datetime
from sellcard.common import Method as mth
from sellcard.common.model import MyError
from django.db import transaction

def index(request):
    rates = request.session.get('s_rates')
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    return render(request, 'card/change/cardChange.html', locals())

@transaction.atomic
def save(request):
    operator = request.session.get('s_uid','')
    shopCode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    #入卡列表
    cardListInStr = request.POST.get('cardListIn','')
    cardListIn = json.loads(cardListInStr)
    #入卡合计
    totalNumIn = request.POST.get('totalNumIn',0)
    totalValIn = request.POST.get('totalValIn',0.00)

    #出卡列表
    cardListOutStr = request.POST.get('cardListOut','')
    cardListOut = json.loads(cardListOutStr)
    #出卡合计
    totalNumOut = request.POST.get('totalNumOut',0)
    totalValOut = request.POST.get('totalValOut',0.00)

    #优惠卡列表
    discListStr = request.POST.get('discList','')
    discList = json.loads(discListStr)
    #优惠返现
    discCash = request.POST.get('discCash',0.00)

    #优惠返点金额
    disc = request.POST.get('disc',0.00)
    # 优惠返点比率
    disRate = request.POST.get('disRate',0.00)
    #优惠补差
    discPay = request.POST.get('discPay',0.00)
    #折扣授权码
    discCode = request.POST.get('discCode','')

    # 支付方式
    payStr = request.POST.get('payStr', '')
    payList = json.loads(payStr)
    hjsStr = request.POST.get('hjsStr', '')
    # 黄金手卡号列表
    hjsList = []
    if len(hjsStr) > 0:
        hjsStr = hjsStr[0:len(hjsStr) - 1]
        hjsList = hjsStr.split(',')

    #买卡人信息
    buyerName = (request.POST.get('buyerName','')).strip()
    buyerPhone = (request.POST.get('buyerPhone','')).strip()

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
            order_sn = 'C'+mth.setOrderSn(OrderChangeCard)
            created_time=datetime.datetime.today()
            cardIsStoreList = []
            cardCommonList = []
            #1、更新cardInventory中入库卡数据
            for card in cardListIn:
                queryCard = CardInventory \
                    .objects \
                    .filter(card_status='2', card_action='0', card_no=card['cardId'], card_value=F('card_blance'))
                cardInventory = queryCard.values('is_store').first()
                if cardInventory:
                    is_store = cardInventory['is_store']

                    if is_store:
                        card['type'] = 2
                        cardIsStoreList.append(card)
                        status = '7'
                        action = '0'
                    else:
                        cardCommonList.append(card)
                        status = '1'
                        action = '1'
                resUpdate = resSave = 0
                #处理老卡换入
                if not cardInventory:
                    obj = CardInventory \
                        .objects \
                        .create(card_no=card['cardId'], card_value=card['cardVal'], card_status='1', card_action='1',
                                card_addtime=datetime.datetime.now(), shop_code=shopCode,
                                is_store=0, card_blance=card['cardVal'])
                    resSave = obj.id
                else:
                    resUpdate = queryCard.update(card_status=status, card_action=action, shop_code=shopCode)
                if (resUpdate == 0 and resSave == 0):
                    raise MyError(card['cardId'] + '状态更新失败')

            #2、保存支付信息
            isThird = False
            payDiscDict = mth.getPayDiscDict()
            ChangePaymentList = []
            for pay in payList:
                orderPay = OrderChangeCardPayment()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                # 处理混合支付的优惠
                is_pay = 1
                if pay['payId'] in ('3', '4'):
                    is_pay = '0'
                elif pay['payId'] == '6':
                    isThird = True
                    is_pay = '0'
                    disRate = payDiscDict[pay['payId']]
                    disc = discCash = float(pay['payVal']) * float(disRate)
                elif pay['payId'] in ('7', '8', '10', '11'):
                    isThird = True
                    disRate = payDiscDict[pay['payId']]
                    disc = discCash = float(pay['payVal']) * float(disRate)
                orderPay.is_pay = is_pay

                if pay['payId'] == '9':
                    isThird = True
                    mth.upChangeCode(hjsList, shopCode)

                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                ChangePaymentList.append(orderPay)
            OrderChangeCardPayment.objects.bulk_create(ChangePaymentList)

            #3、保存order信息
            order = OrderChangeCard()
            order.order_sn = order_sn
            order.operator_id = operator
            order.depart = depart
            order.shop_code = shopCode
            order.user_name = buyerName
            order.user_phone = buyerPhone
            order.total_in_amount = totalNumIn
            order.total_in_price = totalValIn
            order.total_out_amount = totalNumOut
            order.total_out_price = totalValOut
            order.disc_rate = disRate
            order.disc = disc
            order.disc_cash = discCash
            order.disc_pay = discPay
            order.add_time = created_time
            order.save()

            #4、分别创建orderInfo列表
            cardOutInfoList =[]
            changeCardInfoList = []
            cardInIdList = []
            cardCommonIdList=[]
            cardIsStoreIdList = []
            cardCommonInNum=cardIsStoreInNum = 0
            if len(cardCommonList):
                infoCommon = createChangInfoList(cardCommonList,order_sn)
                changeCardInfoList += infoCommon
                cardCommonIdList = [card['cardId'] for card in cardCommonList]
                cardInIdList += cardCommonIdList
                cardCommonInNum = len(cardCommonIdList)
            if len(cardIsStoreList):
                infoIsStore = createChangInfoList(cardIsStoreList, order_sn)
                changeCardInfoList += infoIsStore
                cardIsStoreIdList = [card['cardId'] for card in cardIsStoreList]
                cardInIdList += cardIsStoreIdList
                cardIsStoreInNum = len(cardIsStoreIdList)
            if len(cardListOut):
                infoOut = createChangInfoList(cardListOut,order_sn)
                changeCardInfoList += infoOut
                cardOutInfoList += cardListOut
            if not isThird and len(discList):
                infoDisc = createChangInfoList(cardIsStoreList, discList)
                changeCardInfoList += infoDisc
                cardOutInfoList += discList

            #5、保存orderInfo
            OrderChangeCardInfo.objects.bulk_create(changeCardInfoList)
            #6、更新CardInventory出库卡状态
            cardOutIdList = [card['cardId'] for card in cardOutInfoList]
            cardsOutNum = len(cardOutIdList)
            resCardOut = CardInventory.objects\
                .filter(card_status='1',card_action='1',card_no__in=cardOutIdList,card_value=F('card_blance'),is_store='0')\
                .update(card_status='2',card_action='0')
            if resCardOut != cardsOutNum:
                raise MyError('CardInventory状态更新失败')

            #7、更新折扣授权码信息
            if discCode:
                resCode = mth.updateDisCode(discCode,shopCode,order_sn)
                if resCode == 0:
                    raise MyError('折扣授权码状态更新失败')

            # 8、更新Guest信息
            updateConfList = []
            updateConfList.append({'ids':cardIsStoreIdList,'mode':'7','count':cardIsStoreInNum})
            updateConfList.append({'ids': cardCommonIdList, 'mode': '9', 'count': cardCommonInNum})
            updateConfList.append({'ids':cardOutIdList,'mode':'1','count':cardsOutNum})

            resGuest = mth.updateCard(updateConfList)
            if resGuest['status']==0:
                raise MyError(resGuest['msg'])

            res["status"] = 1
            ActionLog.objects.create(
                action='换卡-单卡', u_name=request.session.get('s_uname'), cards_in=json.dumps(cardInIdList),
                cards_out=json.dumps(cardOutIdList), add_time=datetime.datetime.now()
            )
            del request.session['postToken']
    except Exception as e:
        res["status"] = 0
        if hasattr(e, 'value'):
            res['msg'] = e.value
        ActionLog.objects.create(
            action='换卡-单卡', u_name=request.session.get('s_uname'),
            add_time=datetime.datetime.now(), err_msg=e
        )

    return HttpResponse(json.dumps(res))


def createChangInfoList(cardList,order_sn):
    infoList = []
    for card in cardList:
        orderInfo = OrderChangeCardInfo()
        orderInfo.order_sn = order_sn
        orderInfo.card_no = card['cardId'].strip()
        orderInfo.card_attr = '1'
        orderInfo.card_value = card['cardVal']
        orderInfo.card_balance = card['cardVal']
        if 'type' in card.keys():
            orderInfo.type = card['type']
        infoList.append(orderInfo)
    return infoList


def info(request):
    orderSn = request.GET.get('orderSn','').strip()
    today = datetime.date.today()

    order = OrderChangeCard.objects\
        .values('shop_code', 'depart', 'operator_id', 'order_sn', 'total_in_price', 'total_in_amount',
                    'total_out_price', 'total_out_amount', 'add_time')\
        .filter(order_sn=orderSn)
    infoList = OrderChangeCardInfo.objects.values('card_no', 'card_attr', 'card_value', 'card_balance')\
        .filter(order_sn=orderSn)

    totalNumIn = totalValueIn = totalNumOut = totalValueOut = 0

    if len(order):
        for d in order:
            if d['total_out_price'] > d['total_in_price']:
                isPrint = True
            else:
                isPrint = False
    else:
        err={}
        err['msg']='此订单不存在'
        return render(request, '500.html', locals())

    if len(infoList):
        for info in infoList:
            # 进卡
            if info['card_attr'] == '1':
                totalValueIn += float(info['card_value'])
                totalNumIn += 1
            # 出卡
            if info['card_attr'] == '0':
                totalValueOut += float(info['card_value'])
                totalNumOut += 1
            # 差额
            totalDiff = totalValueOut - totalValueIn
        return render(request, 'common/changeInfo.html', locals())
    else:
        err={}
        err['msg']='此订单不存在'
        return render(request, '500.html', locals())