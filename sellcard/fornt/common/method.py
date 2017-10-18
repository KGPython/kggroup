# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/23 11:48'
import datetime

from sellcard.common import Method as mth
from sellcard.models import OrderPaymentInfo,Orders,OrderInfo,VipOrder


def createPaymentList(payList,order_sn,discountVal,Ycash):
    isThird = False
    payDiscDict = mth.getPayDiscDict()
    oderPaymentList = []
    for pay in payList:
        orderPay = OrderPaymentInfo()
        orderPay.order_id = order_sn
        orderPay.pay_id = pay['payId']
        # 处理混合支付的优惠
        is_pay = 1
        if pay['payId'] == '3':
            is_pay = '0'
        if pay['payId'] == '4':
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
        orderPay.pay_value = pay['payVal']
        orderPay.remarks = pay['payRmarks']
        oderPaymentList.append(orderPay)
    return oderPaymentList,isThird,discountVal,Ycash


def createOrderInfoList(cardList,order_sn,isThird,YcardList):
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
    return orderInfoList


def createOrder(dict):
    order = Orders()
    order.buyer_name = dict['buyerName']
    order.buyer_tel = dict['buyerPhone']
    order.buyer_company = dict['buyerCompany']
    order.total_amount = dict['totalVal'] + dict['discountVal']
    order.paid_amount = dict['totalVal'] + dict['Ybalance']  # 实付款合计=售卡合计+优惠补差
    order.disc_amount = dict['discountVal']  # 优惠合计
    order.diff_price = dict['Ybalance']
    order.shop_code = dict['shopcode']
    order.depart = dict['depart']
    order.operator_id = dict['operator']
    order.action_type = dict['actionType']
    order.add_time = datetime.datetime.now()
    order.discount_rate = dict['discountRate']
    order.order_sn = dict['order_sn']
    order.y_cash = dict['Ycash']
    return order


def createVipOrder(id,order_sn,disc_state):
    order = VipOrder()
    order.vip_id = id
    order.order_sn = order_sn
    order.disc_state = disc_state
    order_state = '0' if disc_state else '1'
    order.order_state = order_state
    return order