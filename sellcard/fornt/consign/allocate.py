# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/21 14:57'

import datetime, json
from django.core.paginator import Paginator  # 分页查询
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from sellcard.common import Method as mth
from sellcard.common.model import MyError
from sellcard.models import CashierList, Shops, CardInventory


def index(request):
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    shops = Shops.objects.values('shop_code','shop_name','city').order_by('shop_code')
    if role in ('1','6','7') :
        shops = shops
    elif role == '8':#承德总部财务
        shops = shops.filter(city='C')
    elif role == '9':#唐山总部财务
        shops = shops.filter(city='T')
    else:
        shops = shops.filter(shop_code=shop)
    shops_len = len(shops)
    if request.method == 'POST':
        shopcode = mth.getReqVal(request, 'shopcode', '')
        keyword = mth.getReqVal(request, 'keyword', '')
        # 表单分页参数开始
        page = mth.getReqVal(request, 'page', 1)
        show_num = mth.getReqVal(request, 'show_num', 8)
        # 表单分页参数结束

        conn = mth.getMysqlConn()
        cur = conn.cursor()
        whereStr = "WHERE t.is_store = 1 "

        if role in ('2', '10'):
            whereStr += " AND t.shop_code ='" + shop + "'"


        if shopcode != '':
            whereStr += " AND t.shop_code ='" + shopcode + "'"
        else:
            shopsCode = ''
            if role == '9':
                shopsCode = mth.getCityShopsCode('T')
                shopsCodeStr = "'" + "','".join(shopsCode) + "'"
                whereStr += " AND t.shop_code IN (" + shopsCodeStr + ")"
            if role == '8':
                shopsCode = mth.getCityShopsCode('C')
                shopsCodeStr = "'" + "','".join(shopsCode) + "'"
                whereStr += " AND t.shop_code IN (" + shopsCodeStr + ")"

        if keyword != '':
            whereStr += " AND (c.username like '%" + keyword + "%' OR c.`name` like '%" + keyword + "%')"

        sql = """
SELECT
	t.shop_code,
	s.shop_name,
	c.username as user_code,
	IFNULL(c.`name`, '未分配') AS username,
	t.card_value,
	count(t.card_no) AS account,
	sum(CASE WHEN t.card_status = 2 THEN 1 ELSE 0 END) AS out_num,
	sum(CASE WHEN t.card_status = 1 THEN 1 ELSE 0 END) AS in_num
FROM
	card_inventory t LEFT JOIN shops s ON t.shop_code = s.shop_code
	LEFT JOIN cashier_list c ON t.shop_code = c.shop_code and t.username = c.username
"""+ whereStr +"""
GROUP BY
	t.shop_code,
	s.shop_name,
	c.username,
	c.`name`,
	t.card_value
                """
        cur.execute(sql)
        List = cur.fetchall()

        # 表单分页开始
        paginator = Paginator(List, show_num)

        try:
            List = paginator.page(page)

            if List.number > 1:
                page_up = List.previous_page_number
            else:
                page_up = 1

            if List.number < List.paginator.num_pages:
                page_down = List.next_page_number
            else:
                page_down = List.paginator.num_pages

        except Exception as e:
            print(e)
            # 表单分页结束

    return render(request, 'consign/list.html', locals())


def detail(request):
    # 在服务端session中添加key认证，避免用户重复提交表单i
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    shop_code = request.session.get('s_shopcode')
    userList= CashierList.objects.values('username', 'name').filter(shop_code=shop_code)
    return render(request, 'consign/detail.html', locals())


@transaction.atomic
def save(request):
    res = {}
    if request.method == 'POST':
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            res["msg"] = 0
            return HttpResponse(json.dumps(res))

        shop_code = request.session.get('s_shopcode')
        name = request.POST.get('name')
        start_no = request.POST.get('start_no')
        end_no = request.POST.get('end_no')
        try:
            with transaction.atomic():
                CardInventory.objects.filter(is_store=1,
                                             shop_code=shop_code,
                                             username=None,
                                             card_no__gte=start_no,
                                             card_no__lte=end_no).update(username=name)

                res['msg'] = 1
                del request.session['postToken']

        except Exception as e:
            print(e)
            res['msg'] = 0

    return HttpResponse(json.dumps(res))

