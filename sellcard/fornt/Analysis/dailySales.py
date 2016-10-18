#-*- coding:utf-8 -*-
"""
__author__:齐旭
__create__:2016-10-18
__introduce__:
日结销量查询:为了方便门店团购经理角色查询门店人员每日售卡情况
"""

#引用框架
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
#引用系统
import datetime
#引用自身项目
from sellcard.common import Method as mth
from sellcard.templatetags import basefilter

@csrf_exempt
def index(request):
    """
    日结销量查询逻辑层
    """

    #定义变量并初始化
    shopcode = request.session.get('s_shopcode') #门店编码
    shop = basefilter.transShopCode(shopcode) #门店名称
    today = str(datetime.date.today()) #当前日期 用于显示

    resList=[] #创建集合用于记录查询结果

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    page = mth.getReqVal(request,'page',1)

    sql =  \
    "SELECT "+\
    "	oi.card_balance, " +\
    "	CASE oi.card_attr " +\
    "      WHEN 1 THEN " +\
    "      	'普通' " +\
    "      WHEN 2 THEN  " +\
    "      	'赠卡' " +\
    "      ELSE  " +\
    "      	'其它' " +\
    "      END AS card_attr, " +\
    "	count(1) AS aomunt,  " +\
    "	oi.card_balance * count(1) AS account " +\
    "FROM  " +\
    "	orders ord,  " +\
    "	order_info oi  " +\
    "WHERE   " +\
    "  ord.shop_code = '"+shopcode+"' " +\
    "AND date_format(ord.add_time,'%Y-%m-%d') = '"+today+"' " +\
    "AND ord.order_sn = oi.order_id  " +\
    "AND oi.card_action = 0  " +\
    "GROUP BY  " +\
    "	oi.card_balance, " +\
    "	oi.card_attr  " +\
    "ORDER BY " +\
    "	oi.card_attr, " +\
    "	oi.card_balance DESC "

    cur.execute(sql)
    list = cur.fetchall()
    resList.extend(list)

    cur.close()
    conn.close()

    sum_amount = 0
    sum_account = 0

    for item in resList:
        sum_amount += item['aomunt']
        sum_account += item['account']

    #返回显示前台页面
    return render(request, 'dailySales.html', locals())