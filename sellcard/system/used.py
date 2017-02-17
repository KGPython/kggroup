# -*- coding:utf-8 -*-
__author__ = 'qixu'
import json

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator  # 分页查询
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from sellcard.common import Method as mth
from sellcard.common.model import MyError
from sellcard.models import AdminUser, Role, Shops


def index(request):
    """
    用户列表controllers
    :param request:
    :return:列表view
    """
    roleList = Role.objects.values().order_by('id')
    shopList = Shops.objects.values().order_by('shop_code')

    shop_code = mth.getReqVal(request, 'shop_code', '')
    depart = mth.getReqVal(request, 'depart', '')
    role = mth.getReqVal(request, 'role', '')
    user_name = mth.getReqVal(request, 'user_name', '')
    # 表单分页参数开始
    page = mth.getReqVal(request, 'page', 1)
    show_num = mth.getReqVal(request, 'show_num', 8)
    # 表单分页参数结束

    kwargs = {}

    if shop_code != '':
        kwargs.setdefault('shop_code', shop_code)

    if depart != '':
        kwargs.setdefault('depart', depart)

    if role != '':
        kwargs.setdefault('role_id', role)

    if user_name != '':
        List = AdminUser.objects.values('id', 'user_name', 'name', 'shop_code', 'depart', 'role_id',
                                        'last_login', 'last_ip').filter(
            Q(user_name__icontains=user_name) | Q(name__icontains=user_name),
            **kwargs).order_by('last_login')
    else:
        List = AdminUser.objects.values('id', 'user_name', 'name', 'shop_code', 'depart', 'role_id',
                                        'last_login', 'last_ip').filter(**kwargs).order_by('last_login')

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

    return render(request, 'system/user/List.html', locals())


def detail(request):
    """
    赊销金券列表controllers
    :param request:
    :return:列表view
    """
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    roleList = Role.objects.values().order_by('id')
    shopList = Shops.objects.values().order_by('shop_code')
    user_id = mth.getReqVal(request, 'user_id', '')
    user_info = []
    if user_id != '':
        user_info = AdminUser.objects.values('user_name', 'name', 'shop_code', 'depart', 'role_id').get(id=user_id)

    return render(request, 'system/user/Detail.html', locals())

def IsExist(user_name):
    return AdminUser.objects.filter(user_name=user_name).count()


def save(request):
    """
    提交用户信息controllers
    :param request:
    :return:json
    """
    res = {}
    if request.method == 'POST':
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            res['status'] = 0
            return HttpResponse(json.dumps(res))

        user_id = request.POST.get('user_id')
        user_name = request.POST.get('user_name')
        name = request.POST.get('name')
        shop_code = request.POST.get('shop_code')
        depart = request.POST.get('depart')
        role_id = request.POST.get('role')

        if user_id == '':
            flag = IsExist(user_name)
            if flag > 0:
                res['status'] = 0
                res['msg'] = '该用户名已存在'
                return HttpResponse(json.dumps(res))

        shop_id = None
        if shop_code != '':
            shop_id = Shops.objects.values('id').get(shop_code=shop_code)['id']
        try:
            with transaction.atomic():
                if user_id == '':
                    createNum = AdminUser.objects.create(user_name=user_name,
                                                         password=mth.md5('1'),
                                                         name=name,
                                                         shop_id=shop_id,
                                                         shop_code=shop_code,
                                                         depart=depart,
                                                         role_id=role_id)


                    if  not createNum.id:
                        raise MyError('新建用户失败！')
                else:
                    updataNum = AdminUser.objects.filter(id=int(user_id)) \
                        .update(name=name,
                                shop_id=shop_id,
                                shop_code=shop_code,
                                depart=depart,
                                role_id=role_id)

                    if updataNum != 1:
                        raise MyError('修改用户失败！')
        except MyError as my_e:
            res['status'] = 0
            res['msg'] = my_e.value
            return HttpResponse(json.dumps(res))
        except Exception as e:
            res['status'] = 0
            res['msg'] = e
            return HttpResponse(json.dumps(res))

        res['status'] = 1
        del request.session['postToken']
    return HttpResponse(json.dumps(res))
