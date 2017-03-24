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
from sellcard.models import Vip, VipBank


def index(request):
    if request.method == 'POST':
        company = mth.getReqVal(request, 'company', '')
        # 表单分页参数开始
        page = mth.getReqVal(request, 'page', 1)
        show_num = mth.getReqVal(request, 'show_num', 8)
        # 表单分页参数结束

        if company != '':
            List = Vip.objects.values('id', 'company', 'person', 'tel', 'add_time').filter(
                Q(company__icontains=company) | Q(person__icontains=company)).order_by('id')
        else:
            List = Vip.objects.values('id', 'company', 'person', 'tel', 'add_time').order_by('id')

        for row in List:
            row['bank_list'] = VipBank.objects.values('id', 'bank_name').filter(vip_id=row['id'])
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

    return render(request, 'vip/manage.html', locals())


def detail(request):
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    vip_id = request.GET.get('vip_id')

    return render(request, 'vip/manageInfo.html', locals())


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

        vip_id = request.POST.get('vip_id')
        company = request.POST.get('company')
        person = request.POST.get('person')
        tel = request.POST.get('tel')
        try:
            with transaction.atomic():
                if vip_id == 'None':
                    Vip.objects.create(company=company,
                                       person=person,
                                       tel=tel,
                                       add_time=datetime.datetime.now())
                else:
                    Vip.objects.filter(id=vip_id).update(company=company, person=person, tel=tel)

                res['msg'] = 1
                del request.session['postToken']

        except Exception as e:
            print(e)
            res['msg'] = 0

    return HttpResponse(json.dumps(res))


def delete(request):
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    vip_id = request.GET.get('vip_id')

    return render(request, 'vip/manageInfo.html', locals())