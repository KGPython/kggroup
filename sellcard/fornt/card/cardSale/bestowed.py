#-*- coding:utf-8 -*-
__author__ = 'admin'

from django.shortcuts import render
from django.db import transaction
import json
from sellcard.models import Orders,OrderInfo,CardInventory,ActionLog,OrderPaymentInfo
import datetime
from sellcard.common import Method as mtu
from django.http import HttpResponse
from sellcard.common.model import MyError

def index(request):
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    return render(request, 'card/sale/bestowed.html', locals())

@transaction.atomic
def saveOrder(request):
    operator = request.session.get('s_uid','')
    shopcode = request.session.get('s_shopcode','')
    depart = request.session.get('s_depart','')

    #售卡列表
    cardStr = request.POST.get('cardsStr','')
    cardList = json.loads(cardStr)

    #合计信息
    discVal = request.POST.get('discVal',0.00)
    discPay = request.POST.get('discPay',0.00)
    remark = request.POST.get('remarks','')
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
            order_sn = 'S'+mtu.setOrderSn()
            #order_info表
            orderInfoList = []
            for card in cardList:
                orderInfo = OrderInfo()
                orderInfo.order_id = order_sn
                orderInfo.card_id = card['cardId'].strip()
                orderInfo.card_balance = float(card['cardVal'])
                orderInfo.card_action = '0'
                orderInfo.card_attr = '2'
                orderInfoList.append(orderInfo)
            OrderInfo.objects.bulk_create(orderInfoList)

            #order_payment_info表
            orderPay = OrderPaymentInfo()
            orderPay.order_id = order_sn
            orderPay.pay_id = 1
            orderPay.is_pay = '1'
            orderPay.pay_value = float(discPay)
            orderPay.save()

            #orders表
            order = Orders()
            order.buyer_name = buyerName
            order.buyer_tel = buyerPhone
            order.buyer_company = buyerCompany
            order.total_amount = 0
            order.paid_amount = float(discPay)
            order.disc_amount = float(discVal)
            order.diff_price = float(discPay)
            order.y_cash =0
            order.shop_code = shopcode
            order.depart = depart
            order.operator_id = operator
            order.action_type = '5'
            order.add_time = datetime.datetime.now()
            order.order_sn = order_sn
            order.remark = remark
            order.save()

            #更新
            cardIdList = []
            for card in cardList:
                cardIdList.append(card['cardId'])
            cardNum = len(cardIdList)

            resCard = CardInventory.objects.filter(card_no__in=cardIdList).update(card_status=2,card_action='0')
            if resCard!= cardNum:
                raise MyError('CardInventory状态更新失败')

            # 更新Guest
            updateConfList = []
            updateConfList.append({'ids': cardIdList, 'mode': '1', 'count': cardNum})
            resGuest = mtu.updateCard(updateConfList)
            if resGuest['status'] == 0:
                raise MyError(resGuest['msg'])

            res["status"] = 1
            res["urlRedirect"] ='/kg/sellcard/fornt/cardsale/orderInfo/?orderSn='+order_sn
            ActionLog.objects.create(action='实物团购返点',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now())
            del request.session['postToken']
    except Exception as e:
        if hasattr(e,'value'):
            res['msg'] = e.value
        res["status"] = 0
        ActionLog.objects.create(action='实物团购返点',u_name=request.session.get('s_uname'),cards_out=cardStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))