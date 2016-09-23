#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Shops,CardType,Payment,Departs
from django.db.models import Q


# 查询门店信息
def findShop(shopcode=None):
    q = Q()
    if shopcode:
        q.add(Q(shop_code=shopcode), Q.AND)

    shopList = Shops.objects.values("id","shop_name", "shop_code").filter(q).order_by('shop_code')
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
        q.add(Q(pay_id=payId), Q.AND)

    PayList = Payment.objects.values("id", "payment_name").filter(q).order_by('id')
    return PayList

def index(request):

    return render(request, "index.html")

def global_setting(request):
    # 加密狗验证服务地址
    SOFTKEY_URL = "http://192.168.250.8:8082/authservice/inf/main"
    return locals()