#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import OrderUpCard,OrderUpCardInfo,CardInventory,ActionLog
from django.http import HttpResponse
from django.core.paginator import Paginator
from sellcard.common import Method as mtu
from django.db import transaction
from sellcard.common.model import MyError
import datetime,json

__EACH_PAGE_SHOW_NUMBER=10

def index(request):

    return render(request, 'card/fill/cardFill.html', locals())

def query(request):
    shopCode = request.session.get('s_shopcode')

    pageNum =mtu.getReqVal(request,"pageNum","1")
    user_phone = request.POST.get("user_phone","")
    state = request.POST.get("state","")

    karrs = {}
    karrs.setdefault("state__in",[0,1])
    if user_phone:
        karrs.setdefault("user_phone__contains",user_phone)
    if state:
        karrs.setdefault("state",state)
    if shopCode:
        karrs.setdefault("shop_code",shopCode)

    order_list = OrderUpCard.objects.values("order_sn","total_amount","total_price","action_type","user_name",
                               "user_phone","state","add_time",)\
        .filter(**karrs)\
        .order_by("-order_sn")

    page = Paginator(order_list, __EACH_PAGE_SHOW_NUMBER, allow_empty_first_page=True).page(int(pageNum))
    result = {"page": page, "pageNum": str(pageNum)}
    result.setdefault("user_phone", user_phone)
    result.setdefault("state", state)
    return render(request, 'card/fill/cardFillQuery.html', result)

@transaction.atomic
def save(request):
    operator_id = request.session.get('s_uid','')
    shopCode = request.session.get('s_shopcode','')

    res = {}
    #入卡列表
    cardInStr = request.POST.get('cardInStr','')
    cardInList = json.loads(cardInStr)
    #入卡合计
    cardInTotalNum = request.POST.get('cardInTotalNum',0)
    cardInTotalVal = request.POST.get('cardInTotalVal',0.00)

    #补卡人信息
    user_name = (request.POST.get('user_name','')).strip()
    user_phone = (request.POST.get('user_phone','')).strip()
    action_type = (request.POST.get('action_type','')).strip()

    try:
        with transaction.atomic():
            order_sn = 'F'+setOrderSn()
            order = OrderUpCard()
            order.order_sn=order_sn
            order.action_type=action_type
            order.total_amount=cardInTotalNum
            order.total_price=cardInTotalVal
            order.user_name=user_name
            order.user_phone=user_phone
            order.state=1
            order.shop_code=shopCode
            # order.operator_id=operator_id
            order.created_id=operator_id
            order.add_time=datetime.datetime.today()
            order.save()

            #订单明细：入卡,待补的卡即待作废的卡
            cardIdInList = []
            for card in cardInList:
                info = OrderUpCardInfo()
                info.order_sn=order_sn
                info.card_no=card["cardId"].strip()
                info.card_value=card["cardVal"]
                info.card_balance=card["balance"]
                info.card_attr=1
                info.created_time=datetime.datetime.today()
                info.save()

                cardIdInList.append(card['cardId'])

            #冻结旧卡
            CardInventory.objects.filter(card_no__in=cardIdInList).update(card_status=4)
            ActionLog.objects.create(action='补卡-补卡',u_name=request.session.get('s_uname'),cards_in=cardInStr,add_time=datetime.datetime.now())
            res["status"] = 1
            res["urlRedirect"] = '/kg/sellcard/fornt/cardfill/query/'
    except Exception as e:
        print(e)
        res["status"] = 0
        res["msg"] = e
        ActionLog.objects.create(action='补卡-补卡',u_name=request.session.get('s_uname'),cards_in=cardInStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))

def setOrderSn():
    start = datetime.date.today().strftime('%Y-%m-%d 00:00:00')
    end = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    count  = OrderUpCard.objects.filter(add_time__gte=start,add_time__lte=end).count()+1
    if count<10:
        sn = datetime.date.today().strftime('%y%m%d')+'000'+str(count)
    elif count>=10 and count<100:
        sn = datetime.date.today().strftime('%y%m%d')+'00'+str(count)
    elif count>=100 and count<1000:
        sn = datetime.date.today().strftime('%y%m%d')+'0'+str(count)
    elif count>=1000 and count<10000:
        sn = datetime.date.today().strftime('%y%m%d')+str(count)
    return sn

def gotcard(request):
    order_sn = mtu.getReqVal(request,"order_sn","")

    if order_sn:
        try:
            order = OrderUpCard.objects.values("order_sn","total_amount","total_price","action_type","user_name",
                               "user_phone","state","add_time",).get(order_sn=order_sn)
            orderInfoList = OrderUpCardInfo.objects.values("card_no","card_value","card_balance",).filter(order_sn=order_sn,card_attr=1)
        except Exception as e:
            print(e)
    return render(request, 'card/fill/cardFillModify.html', locals())

def update(request):
    operator_id = request.session.get('s_uid', '')
    depart = request.session.get('s_depart','')
    res = {}
    # 出卡列表
    cardOutStr = request.POST.get('cardOutStr', '')
    cardOutList = json.loads(cardOutStr)
    # 出卡合计
    cardOutTotalNum = request.POST.get('cardOutTotalNum', 0)
    cardOutTotalVal = request.POST.get('cardOutTotalVal', 0.00)

    order_sn = request.POST.get('order_sn', '')
    paymoney = request.POST.get('paymoney', '')

    try:
        with transaction.atomic():
            #更新订单信息
            OrderUpCard.objects.filter(order_sn=order_sn)\
                .update(fill_amount=cardOutTotalNum,fill_price=cardOutTotalVal,diff_price=paymoney,state=0,operator_id=operator_id,depart=depart,modified_time=datetime.datetime.today())
            # 订单明细：入卡,待补的卡即待作废的卡
            cardIdOutList = []
            for card in cardOutList:
                info = OrderUpCardInfo()
                info.order_sn = order_sn
                info.card_no = card["cardId"].strip()
                info.card_value = card["cardVal"]
                info.card_balance = card["balance"]
                info.card_attr =2
                info.created_time = datetime.datetime.today()
                info.save()

                cardIdOutList.append(card['cardId'])

            # 激活新卡
            cardOutNum = len(cardIdOutList)
            resCardOut = CardInventory.objects.filter(card_no__in=cardIdOutList).update(card_status=2,card_action=0)
            if resCardOut != cardOutNum:
                raise MyError('CardInventory状态更新失败')

            # 更新Guest
            updateConfList = []
            updateConfList.append({'ids': cardIdOutList, 'mode': '1', 'count': cardOutNum})
            resGuest = mtu.updateCard(updateConfList)
            if resGuest['status'] == 0:
                raise MyError(resGuest['msg'])

            res["status"] = 1
            res['urlRedirect'] = '/kg/sellcard/fornt/cardfill/query/'
            ActionLog.objects.create(action='补卡-领卡',u_name=request.session.get('s_uname'),cards_out=cardOutStr,add_time=datetime.datetime.now())

    except Exception as e:
        res["status"] = 0
        if hasattr(e,'value'):
            res['msg'] = e.value
        ActionLog.objects.create(action='补卡-领卡',u_name=request.session.get('s_uname'),cards_out=cardOutStr,add_time=datetime.datetime.now(),err_msg=e)

    return HttpResponse(json.dumps(res))


def info(request):
    order_sn = mtu.getReqVal(request,"order_sn","")
    if order_sn:
        try:
            order = OrderUpCard.objects.values("order_sn","total_amount","total_price","action_type","user_name",
                               "user_phone","state","add_time","fill_price","fill_amount","diff_price").get(order_sn=order_sn)
            cardInList = OrderUpCardInfo.objects.values("card_no","card_value","card_balance",).filter(order_sn=order_sn,card_attr=1)
            cardOutList = OrderUpCardInfo.objects.values("card_no", "card_value", "card_balance", ).filter(order_sn=order_sn, card_attr=2)
            diff_amount = order["fill_price"] - order["total_price"]
        except Exception as e:
            print(e)
    return render(request, 'card/fill/cardFillInfo.html', locals())

