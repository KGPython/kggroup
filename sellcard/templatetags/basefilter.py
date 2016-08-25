#-*- coding:utf-8 -*-
__author__ = 'liubf'
from django import template
from sellcard import views as base
from sellcard.models import AdminUser
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

#门店编号转名称
@register.filter
def transShopId(key):
    shopList = base.findShop()
    shopname = ''
    for shop in shopList:
        if shop['id']==key:
            shopname = shop['shop_name']
    return shopname

#部门编号转名称
@register.filter
def transDepartCode(key):
    departList = base.findDepart()
    departname = ''
    for depart in departList:
        if depart['depart_id']==key:
            departname = depart['depart_name']
    return departname
#交易类型编号转名称
@register.filter
def transActionType(key):
    ActionType = ''
    if key=='1':
        ActionType = '单卡售卡'
    elif key=='2':
        ActionType = '批量售卡'
    elif key=='3':
        ActionType = '借卡'
    elif key=='4':
        ActionType = ''
    elif key=='5':
        ActionType = '实物团购返点'
    return ActionType

#userid转username
@register.filter
def transUserId(key):
    user = AdminUser.objects.values('name').filter(id=key)
    return user[0]['name']

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
    print(type(v1),type(v2))
    if v1 == '':
        v1 = 0.00
    if v2 == '':
        v2 = 0.00
    res = (float(v1) / float(v2))*100
    return str(round(res,2))+'%'

#转百分比
@register.filter
def add(v1,v2):
    return float(v1) + float(v2)

#减法：v1 - v2
@register.filter
def subtract(v1,v2):
    return float(v1) - float(v2)



