#-*- coding:utf-8 -*-
__author__ = 'liubf'
from django import template
from sellcard import views as base
register = template.Library()

#门店编号转名称
@register.filter
def transShopCode(key):
    shopList = base.findShop()
    shopname = ''
    for shop in shopList:
        if shop['shop_code']==key:
            shopname = shop['shop_name']
    return shopname

#支付编号转名称
@register.filter
def transPayCode(key):
    payList = base.findPays()
    payname = ''
    for pay in payList:
        if pay['id']==key:
            payname = pay['payment_name']
    return payname

#卡状态编号转名称
@register.filter
def transCardStu(key):
    status = ''
    if key=='1':
        status = '未激活'
    elif key=='2':
        status = '已激活'
    elif key=='3':
        status = '已冻结'
    elif key=='4':
        status = '已作废'
    return status

#转百分比
@register.filter
def divide(v1,v2):
    res = (float(v1) / float(v2))*100
    return str(round(res,2))+'%'


