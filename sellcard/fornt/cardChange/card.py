#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
from sellcard.models import CardInventory, OrderChangeCard, OrderChangeCardInfo,ActionLog, OrderChangeCardPayment
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from sellcard.common import Method as mth
from sellcard.common.model import MyError
from django.db import transaction

def index(request):
    rates = request.session.get('s_rates')
    return render(request,'cardChange.html',locals())

@csrf_exempt
@transaction.atomic

def save(request):
    operator = request.session.get('s_uid','')
    shopCode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    res = {}

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
    try:
        with transaction.atomic():
            order_sn = 'C'+mth.setOrderSn(OrderChangeCard)
            created_time=datetime.datetime.today()
            # 保存
            for cardIn in cardListIn:
                orderInfo = OrderChangeCardInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = cardIn['cardId'].strip()
                orderInfo.card_attr = '1'
                orderInfo.card_value = cardIn['cardVal']
                orderInfo.card_balance = cardIn['cardVal']
                orderInfo.add_time = created_time
                orderInfo.save()
            for cardOut in cardListOut:
                orderInfo = OrderChangeCardInfo()
                orderInfo.order_sn = order_sn
                orderInfo.card_no = cardOut['cardId'].strip()
                orderInfo.card_attr = '0'
                orderInfo.card_value = cardOut['cardVal']
                orderInfo.card_balance = cardOut['cardVal']
                orderInfo.save()
            for Ycard in discList:
                YorderInfo = OrderChangeCardInfo()
                YorderInfo.order_sn = order_sn
                YorderInfo.card_no = Ycard['cardId'].strip()
                YorderInfo.card_value = Ycard['cardVal']
                YorderInfo.card_balance = Ycard['cardVal']
                YorderInfo.card_attr = '0'
                YorderInfo.is_disc = '1'
                YorderInfo.save()

            for pay in payList:
                orderPay = OrderChangeCardPayment()
                orderPay.order_id = order_sn
                orderPay.pay_id = pay['payId']
                if pay['payId'] == '4':
                    orderPay.is_pay = '0'
                else:
                    orderPay.is_pay = '1'
                if pay['payId'] == '9':
                    mth.upChangeCode(hjsList, shopCode)

                orderPay.pay_value = pay['payVal']
                orderPay.remarks = pay['payRmarks']
                orderPay.save()

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
            order.disc_rate =disRate
            order.disc = disc
            order.disc_cash = discCash
            order.disc_pay = discPay
            order.add_time = created_time
            order.save()

            #更新
            cardIdInList = []
            for card in cardListIn:
                cardIdInList.append(card['cardId'])
            cardIdOutList = []
            temp = cardListOut+discList
            for card in temp:
                cardIdOutList.append(card['cardId'])
            cardsOutNum = len(cardIdOutList)
            cardsInNum = len(cardIdInList)

            resCardIn = CardInventory.objects.filter(card_no__in=cardIdInList).update(card_status='1',card_action='1')
            resCardOut = CardInventory.objects.filter(card_no__in=cardIdOutList).update(card_status='2',card_action='0')
            if resCardIn != cardsInNum or resCardOut != cardsOutNum:
                raise MyError('系统数据库卡状态更新失败')

            resErpOut = mth.updateCard(cardIdOutList,'1')
            resErpIn = mth.updateCard(cardIdInList,'9')
            if resErpIn != cardsInNum or resErpOut != cardsOutNum:
                mth.updateCard(cardIdOutList,'9')
                mth.updateCard(cardIdOutList,'1')
                raise MyError('ERP数据库卡状态更新失败')

            if discCode:
                resCode = mth.updateDisCode(discCode,shopCode,order_sn)
                if resCode == 0:
                    raise MyError('折扣授权码状态更新失败')

            res["msg"] = 1
            # res["urlRedirect"] = '/kg/sellcard/cardsale/orderInfo/?orderSn=' + order_sn
            ActionLog.objects.create(action='换卡-单卡',u_name=request.session.get('s_uname'),cards_in=cardListInStr,cards_out=cardListOutStr,add_time=datetime.datetime.now())
    except Exception as e:
        res["msg"] = 0
        res["msg_err"] = e.value
        ActionLog.objects.create(action='换卡-单卡',u_name=request.session.get('s_uname'),cards_in=cardListInStr,cards_out=cardListOutStr,add_time=datetime.datetime.now(),err_msg=e.value)

    return HttpResponse(json.dumps(res))
