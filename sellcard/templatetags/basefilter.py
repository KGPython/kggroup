#-*- coding:utf-8 -*-
__author__ = 'liubf'
from django import template
from sellcard import views as base
register = template.Library()

@register.filter
def transShopCode(key):
    shopList = base.findShop()
    shopname = ''
    for shop in shopList:
        if shop['shop_code']==key:
            shopname = shop['shop_name']
    return shopname

@register.filter
def transPayCode(key):
    payList = base.findPays()
    payname = ''
    for pay in payList:
        if pay['id']==key:
            payname = pay['payment_name']
    return payname

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


