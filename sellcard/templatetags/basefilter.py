#-*- coding:utf-8 -*-
__author__ = 'liubf'
from django import template
from sellcard import views as base
from sellcard.models import AdminUser
register = template.Library()

#门店编号转名称
@register.filter
def transShopCode(key):
    shopname = ''
    if(key):
        shop = base.findShop(key)[0]
        shopname = shop['shop_name']
    return shopname

#门店编号转门店电话
@register.filter
def transShopCodeToTel(key):
    shopTel = ''
    if key:
        shop = base.findShop(key)[0]
        shopTel = shop['tel']
    return shopTel


#门店编号转名称
@register.filter
def transShopId(key):
    shopname = ''
    if key:
        shop = base.findShop(key)[0]
        shopname = shop['shop_name']
    return shopname

#部门编号转名称
@register.filter
def transDepartCode(key):
    departname = ''
    if key:
        depart = base.findDepart(key)[0]
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
    if key:
        user = AdminUser.objects.values('name').filter(id=key)
        return user[0]['name']
    else:
        return ''

#支付编号转名称
@register.filter
def transPayCode(key):
    payname = ''
    if key:
        pay =base.findPays(key)[0]
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

@register.filter
def rmbUpper(arg):
    """
    人名币小写转大写，整数部分处理到万亿,小数部分只处理2位
    """
    map  = ["零","壹","贰","叁","肆","伍","陆","柒","捌","玖"]
    unit = ["分","角","元","拾","佰","仟","万","拾","佰","仟","亿",
            "拾","佰","仟","万","拾","佰","仟","兆"]
    nums = []   #取出每一位数字，整数用字符方式转换避大数出现误差
    if type(arg) is float:
        for i in range(len(unit)-3, -3, -1):
            if arg >= 10**i or i < 1:
                nums.append(int(str(arg/(10**i)).split('.')[0])%10)
    else:
        nums = [int(i) for i in str(arg)+'00']

    words = []
    zflag = 0   #标记连续0次数，以删除万字，或适时插入零字
    start = len(nums)-3
    for i in range(start, -3, -1):   #使i对应实际位数，负数为角分
        if 0 != nums[start-i] or len(words) == 0:
            if zflag:
                words.append(map[0])
                zflag = 0
            words.append(map[nums[start-i]])
            words.append(unit[i+2])
        elif 0 == i or (0 == i%4 and zflag < 3): #控制‘万/元’
            words.append(unit[i+2])
            zflag = 0
        else:
            zflag += 1

    if words[-1] != unit[0]:    #结尾非‘分’补整字
        words.append("整")
    return ''.join(words)


