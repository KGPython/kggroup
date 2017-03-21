# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/21 14:57'
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
from sellcard.models import Vip, VipBank


def index(request):
    if request.method == 'POST':
        company = mth.getReqVal(request, 'company', '')
        # 表单分页参数开始
        page = mth.getReqVal(request, 'page', 1)
        show_num = mth.getReqVal(request, 'show_num', 8)
        # 表单分页参数结束

        if company != '':
            List = Vip.objects.values('id', 'company', 'name', 'tel', 'add_time').filter(
                Q(company__icontains=company) | Q(name__icontains=company)).order_by('id')
        else:
            List = Vip.objects.values('id', 'company', 'name', 'tel', 'add_time').order_by('id')


        for row in List:
            row['bank_list'] = VipBank.objects.values('id', 'bank_name').filter(vip_id = row['id'])
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