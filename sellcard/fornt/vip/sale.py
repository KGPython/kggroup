# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/21 14:56'
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse

import json,datetime

from sellcard.common.model import MyError
from sellcard.common import Method as mth
from sellcard.models import OrderPaymentInfo,OrderInfo,CardInventory,ActionLog,Vip
from sellcard.fornt.common import  method as cardMethod

def index(request):
    if request.method == 'POST':
        path = request.path
        operator = request.session.get('s_uid', '')
        shopcode = request.session.get('s_shopcode', '')
        depart = request.session.get('s_depart', '')
        actionType = request.POST.get('actionType', '')
        # 售卡列表
        cardStr = request.POST.get('cardStr', '')
        cardList = json.loads(cardStr)
        # 支付方式
        payStr = request.POST.get('payStr', '')
        payList = json.loads(payStr)
        hjsStr = request.POST.get('hjsStr', '')
        # 合计信息
        totalVal = float(request.POST.get('totalVal', 0.00))
        #折扣
        discountRate = float(request.POST.get('discount', 0.00)) / 100
        disCode = request.POST.get('disCode', '')
        discountVal = float(request.POST.get('discountVal', ''))
        Ybalance = float(request.POST.get('Ybalance', 0.00))
        YcardStr = request.POST.get('YcardStr', '')
        YcardList = json.loads(YcardStr)
        Ycash = request.POST.get('Ycash', '')
        # 顾客信息
        vip_person = request.POST.get('buyerName', '')
        vip_tel = request.POST.get('buyerPhone', '')
        vip_company = request.POST.get('buyerCompany', '')
        vip_id = request.POST.get('vipId', '')
        disc_state = request.POST.get('discState', '')

        order_sn = ''
        res = {}
        try:
            Token = request.session.get('postToken', default=None)
            userToken = request.POST.get('postToken', '')
            if userToken != Token:
                raise MyError('表单重复提交，刷新页面后，重试！')

            with transaction.atomic():
                order_sn = 'S' + mth.setOrderSn()
                #支付相关处理

                oderPaymentList, isThird, discountVal, Ycash = cardMethod.createPaymentList(payList, order_sn, discountVal, Ycash)
                OrderPaymentInfo.objects.bulk_create(oderPaymentList)
                # 保存OrderInfo
                orderInfoList = cardMethod.createOrderInfoList(cardList, order_sn, isThird, YcardList)
                OrderInfo.objects.bulk_create(orderInfoList)
                # 保存Order
                orderData = {
                    'buyerName':vip_person,'buyerPhone':vip_tel,'buyerCompany':vip_company,
                    'totalVal':totalVal,'discountVal':discountVal,'Ybalance':Ybalance,
                    'shopcode':shopcode,'depart':depart,'operator':operator,'actionType':actionType,
                    'discountRate':discountRate,'order_sn':order_sn,'Ycash':Ycash
                }
                order = cardMethod.createOrder(orderData)
                order.save()

                vipOrder = cardMethod.createVipOrder(vip_id,order_sn,disc_state)
                vipOrder.save()

                # 获取所有出卡列表
                cardListTotal = cardList + YcardList
                cardIdList = []
                for card in cardListTotal:
                    cardIdList.append(card['cardId'])
                cardsNum = len(cardIdList)

                # 更新kggroup内部卡状态
                resCard = CardInventory.objects.filter(card_no__in=cardIdList, card_status='1', is_store='0') \
                    .update(card_status='2', card_action='0')
                if resCard != cardsNum:
                    raise MyError('CardInventory状态更新失败')
                # 更新折扣授权码校验码状态
                if disCode:
                    resCode = mth.updateDisCode(disCode, shopcode, order_sn)
                    if resCode == 0:
                        raise MyError('折扣授权码状态更新失败')
                # 更新Guest
                updateConfList = []
                updateConfList.append({'ids': cardIdList, 'mode': '1', 'count': cardsNum})
                resGuest = mth.updateCard(updateConfList)
                if resGuest['status'] == 0:
                    raise MyError(resGuest['msg'])

                res["status"] = 1
                res["urlRedirect"] = '/kg/sellcard/fornt/cardsale/orderInfo/?orderSn=' + order_sn
                ActionLog.objects.create(url=path, u_name=request.session.get('s_uname'),
                                         cards_out=json.dumps(cardIdList), add_time=datetime.datetime.now())
                del request.session['postToken']
        except Exception as e:
            if hasattr(e, 'value'):
                res['msg'] = e.value
            res["status"] = 0
            ActionLog.objects.create(url=path, u_name=request.session.get('s_uname'), add_time=datetime.datetime.now(),
                                     err_msg=e)

        return HttpResponse(json.dumps(res))
    if request.method == 'GET':
        vip_id = request.GET.get('vip_id')
        buyer = Vip.objects.filter(id=vip_id,status='1').values('company', 'person', 'tel','id').first()
        token = 'allow'
        request.session['postToken'] = token

    return render(request, 'vip/sale.html', locals())



