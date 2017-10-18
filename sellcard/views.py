#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Shops,CardType,Payment,Departs
from django.db.models import Q


# 查询门店信息
def findShop(shopcode=None):
    q = Q()
    if shopcode:
        q.add(Q(shop_code=shopcode), Q.AND)
    shopList = Shops.objects.values("id","shop_name","shop_code","tel").filter(q).order_by('shop_code')
    return shopList
# 查询门店信息

def findDepart(depart_id=None):
    q = Q()
    if depart_id:
        q.add(Q(depart_id=depart_id), Q.AND)

    DepartList = Departs.objects.values("depart_id", "depart_name").filter(q).order_by('depart_id')
    return DepartList

# 查询卡类型
def findCardType(cardTypeCode=None):
    q = Q()
    if cardTypeCode:
        q.add(Q(card_type_code=cardTypeCode), Q.AND)

    cardList = CardType.objects.values("card_type_name").filter(q)
    return cardList

# 查询部门信息
def findPays(payId=None):
    q = Q()
    if payId:
        q.add(Q(id=payId,flag='0'), Q.AND)

    PayList = Payment.objects.values("id", "payment_name").filter(q).order_by('id')
    return PayList


from sellcard.models import Orders
def index(request):
    # data = OrderPaymentInfo.objects.get(order__order_sn='S1609240003')
    # print(data.pay.payment_name)
    # print(data.order.add_time)
    # querySet = Orders.objects.filter(b__is_pay='1')
    # print(querySet)
    # order = Orders.objects.get(order_sn='S1609240003')
    # payList = order.orderpaymentinfo_set.all()
    # print(payList)
    # data = Orders.objects.filter(o__is_pay='1',order_sn='S1609240003')
    # print(data)
    return render(request, "index.html")

def global_setting(request):
    # 加密狗验证服务地址
    SOFTKEY_URL = "http://192.168.250.8:8082/authservice/inf/main"
    return locals()


from sellcard.models import OrderPaymentInfo

# Create your tests here.
def test():
    data = OrderPaymentInfo.objects.get(id=10)
    print(data)
