# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
from django.db.models import Count
import datetime, hashlib
from random import sample
from sellcard.models import KfJobsCouponSn


@transaction.atomic
def index(request):
    """
    检验券真伪controllers
    :param request:
    :return:
    """
    batch = request.POST.get('batch', '')
    begin_no = request.POST.get('begin_no', '')
    end_no = request.POST.get('end_no', '')
    kwargs = {}

    if batch != '':
        kwargs.setdefault('batch', batch)

    if begin_no != '':
        kwargs.setdefault('sn__gte', begin_no)

    if end_no != '':
        kwargs.setdefault('sn__lte', end_no)

    List = KfJobsCouponSn.objects.filter(**kwargs).values("request_shop").annotate(total=Count("voucher")).all()


    return render(request, 'voucher/report/index.html', locals())
