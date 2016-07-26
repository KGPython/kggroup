#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Shops,CardType
from django.db.models import Q


# 查询门店信息
def findShop(shopcode=None):
    q = Q()
    if shopcode:
        q.add(Q(shopcode=shopcode), Q.AND)

    shopList = Shops.objects.values("shop_name", "shop_code").filter(q).order_by('shop_code')
    return shopList

# 查询卡类型
def findCardType(cardTypeCode=None):
    q = Q()
    if cardTypeCode:
        q.add(Q(card_type_code=cardTypeCode), Q.AND)

    cardList = CardType.objects.values("card_type_name").filter(q)
    return cardList

def index(request):

    return render(request, "index.html")

def global_setting(request):
    # 加密狗验证服务地址
    SOFTKEY_URL = "http://192.168.250.8:8082/authservice/inf/main"
    return locals()