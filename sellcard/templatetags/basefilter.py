# -*- coding:utf-8 -*-
__author__ = 'liubf'
from django import template
from sellcard import views as base
from sellcard.models import AdminUser, Shops, Departs, Role

register = template.Library()


# =============系统管理begin==================
# 部门编码转文字
@register.filter
def transDepart(key):
    depart = ''
    if (key):
        departs = Departs.objects.values("depart_name").filter(depart_id=key)
        if departs:
            depart = departs[0]['depart_name']
        else:
            depart = '查无ID为:' + key + '角色'
    return depart


# 角色id转名称
@register.filter
def transRole(key):
    role = ''
    if (key):
        roles = Role.objects.values("role_name").filter(id=key)
        if roles:
            role = roles[0]['role_name']
        else:
            role = '查无ID为:' + key + '角色'
    return role


# =============系统管理end==================
# 门店编号转名称
@register.filter
def transShopCode(key):
    shopname = ''
    if (key):
        shop = base.findShop(key)[0]
        shopname = shop['shop_name']
    return shopname


# 门店编号转门店电话
@register.filter
def transShopCodeToTel(key):
    shopTel = ''
    if key:
        shop = base.findShop(key)[0]
        shopTel = shop['tel']
    return shopTel


# 门店编号转名称
@register.filter
def transShopId(key):
    shopname = ''
    if key:
        shop = base.findShop(key)[0]
        shopname = shop['shop_name']
    return shopname


@register.filter
def transShopIdByName(key):
    """
    门店ID转名称
    :author Qixu
    :create 2016/11/28
    :param key:商店ID
    :return:shopname:商店名
    """
    shopname = ''

    if key == 'factory':
        shopname = '供应商'
    elif key == 'outside':
        shopname = '外部出库'
    elif key == 'inside':
        shopname = '内部出库'
    elif key:
        shop = Shops.objects.values("shop_name").filter(id=key)
        if shop:
            shopname = shop[0]['shop_name']
        else:
            shopname = '查无ID为:' + key + '商店'

    return shopname


@register.filter
def transCouponTypeByChinese(key):
    """
    代金券类型转中文
    :author Qixu
    :create 2016/11/28
    :param key:类型编号
    :return:chinese:对应中文含义
    """
    chinese = ''

    if key == 1:
        chinese = '换卡券'
    elif key == 2:
        chinese = '提货券'
    elif key == 3:
        chinese = '通用券'

    return chinese


@register.filter
def transCouponTypeByEnglish(key):
    """
    代金券类型转字母
    :author Qixu
    :create 2016/11/28
    :param key:类型编号
    :return:english:对应字母
    """
    english = ''

    if key == 1:
        english = 'A'
    elif key == 2:
        english = 'B'
    elif key == 3:
        english = 'C'

    return english


# 部门编号转名称
@register.filter
def transDepartCode(key):
    departname = ''
    if key:
        depart = base.findDepart(key)[0]
        departname = depart['depart_name']
    return departname


# 交易类型编号转名称
@register.filter
def transActionType(key):
    ActionType = ''
    if key == '1':
        ActionType = '单卡售卡'
    elif key == '2':
        ActionType = '批量售卡'
    elif key == '3':
        ActionType = '借卡'
    elif key == '4':
        ActionType = ''
    elif key == '5':
        ActionType = '实物团购返点'
    return ActionType


# userid转username
@register.filter
def transUserId(key):
    if key:
        user = AdminUser.objects.values('name').filter(id=key)
        return user[0]['name']
    else:
        return ''


# 支付编号转名称
@register.filter
def transPayCode(key):
    payname = ''
    if key:
        pay = base.findPays(key)[0]
        payname = pay['payment_name']
    return payname


# 卡状态编号转名称
@register.filter
def transCardStu(key):
    status = ''
    if key == '1':
        status = '未激活'
    elif key == '2':
        status = '已激活'
    elif key == '3':
        status = '已冻结'
    elif key == '4':
        status = '已作废'
    return status


# 转百分比
@register.filter
def divide(v1, v2):
    res = 0
    if v2:
        if v1 == '':
            v1 = 0.00
        res = (float(v1) / float(v2)) * 100

    return str(round(res, 2)) + '%'


@register.filter
def o_index(v_i, v_o):
    return v_o[int(v_i)]


@register.filter
def o_column(v_o, v_s):
    return v_o[str(v_s)]


# 转百分比
@register.filter
def add(v1, v2):
    return float(v1) + float(v2)


# 乘法
@register.filter
def multiply(v1, v2):
    return float(v1) * float(v2)


# 减法：v1 - v2
@register.filter
def subtract(v1, v2):
    return float(v1) - float(v2)


@register.filter
def rmbUpper(arg):
    """
    人名币小写转大写，整数部分处理到万亿,小数部分只处理2位
    """
    map = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
    unit = ["分", "角", "元", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿",
            "拾", "佰", "仟", "万", "拾", "佰", "仟", "兆"]
    nums = []  # 取出每一位数字，整数用字符方式转换避大数出现误差
    if type(arg) is float:
        for i in range(len(unit) - 3, -3, -1):
            if arg >= 10 ** i or i < 1:
                nums.append(int(str(arg / (10 ** i)).split('.')[0]) % 10)
    else:
        nums = [int(i) for i in str(arg) + '00']

    words = []
    zflag = 0  # 标记连续0次数，以删除万字，或适时插入零字
    start = len(nums) - 3
    for i in range(start, -3, -1):  # 使i对应实际位数，负数为角分
        if 0 != nums[start - i] or len(words) == 0:
            if zflag:
                words.append(map[0])
                zflag = 0
            words.append(map[nums[start - i]])
            words.append(unit[i + 2])
        elif 0 == i or (0 == i % 4 and zflag < 3):  # 控制‘万/元’
            words.append(unit[i + 2])
            zflag = 0
        else:
            zflag += 1

    if words[-1] != unit[0]:  # 结尾非‘分’补整字
        words.append("整")
    return ''.join(words)


@register.filter
def toCardType(val):
    dict = {'1':'储值卡','2':'挂售卡','3':'春节卡','4':'生日卡','9':'会员卡'}
    return  dict[val]


@register.filter
def truncate_chars(value,len):
    if value.__len__() > len:
        return '%s......'% value[0:len]
    else:
        return value
