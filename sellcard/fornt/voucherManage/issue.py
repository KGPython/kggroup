# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import datetime, time, json
from random import sample
from sellcard.common import Method as mth
from sellcard.models import KfJobsCoupon


@csrf_exempt
@transaction.atomic
def index(request):
    """
    发行代金券列表controllers
    :param request:
    :return:列表view
    """
    shopid = request.session.get('s_shopid')
    today = str(datetime.date.today())
    couponType = mth.getReqVal(request, 'couponType', '')
    printed = mth.getReqVal(request, 'printed', '')
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request, 'page', 1)

    kwargs = {}
    # kwargs.setdefault('shopid', shopid)

    if couponType != '':
        kwargs.setdefault('coupontypeid', couponType)

    if printed != '':
        kwargs.setdefault('flag', printed)

    if start != '':
        kwargs.setdefault('startdate__gte', start)

    if end != '':
        kwargs.setdefault('startdate__lte', endTime)

    #用于全部打印时传入的券号列表
    snlist = str(KfJobsCoupon.objects.values_list('couponno',flat=True).filter(**kwargs))

    resList = KfJobsCoupon.objects.values(
        'shopid', 'createuserid', 'coupontypeid', 'startdate', 'couponno', 'value',
        'giftvalue', 'goodsremark').filter(**kwargs).order_by('shopid', 'startdate', 'createuserid')

    paginator = Paginator(resList, 8)
    try:
        resList = paginator.page(page)
    except Exception as e:
        print(e)

    return render(request, 'voucher/issue/List.html', locals())


@csrf_exempt
@transaction.atomic
def create(request):
    """
    新建代金券
    :param request:
    :return: 新建页view
    """
    if request.method == 'POST':
        shop = request.session.get("s_shopid")
        if shop is None:
            shop = '9999'
        shopCode = request.session.get("s_shopcode")
        user = request.session.get("s_uid")
        amount = request.POST.get('amount')
        type = request.POST.get('type', '1')
        costValue = request.POST.get('costValue')
        giftValue = request.POST.get('giftValue')
        discount = request.POST.get('discount', '0')
        endDate = request.POST.get('endDate')
        CPwdFlag = request.POST.get('CPwdFlag', '0')
        CPwd = request.POST.get('CPwd')
        maxUseTime = request.POST.get('maxUseTime', '1')
        goodsRemark = request.POST.get('goodsRemark')

        str = ''
        if shopCode[0:1] == 'C':
            str = '88814' + shopCode[2:] + datetime.datetime.now().strftime('%y%m%d')
        elif shopCode[0:1] == 'T':
            str = '88815' + shopCode[2:] + datetime.datetime.now().strftime('%y%m%d')
        else:
            str = '8889999' + datetime.datetime.now().strftime('%y%m%d')
        List = set()
        while len(List) < int(amount):
            sn = ''.join(sample('0123456789', 6))
            List.add(sn)

        for var_sn in List:
            KfJobsCoupon.objects.create(shopid=shop,
                                        couponno=str + var_sn,
                                        coupontypeid=type,
                                        startdate=datetime.datetime.now(),
                                        enddate=datetime.datetime.strptime(endDate, "%Y-%m-%d").date(),
                                        cpwdflag=CPwdFlag,
                                        cpwd=CPwd,
                                        usetime=0,
                                        maxusetime=maxUseTime,
                                        value=costValue,
                                        giftvalue=giftValue,
                                        discount=discount,
                                        flag=0,
                                        fromsheettype=220,
                                        goodsremark=goodsRemark,
                                        createuserid=user,
                                        serialid=var_sn,
                                        clearflag=0,
                                        clearvalue=0)
        msg = 1
    return render(request, 'voucher/issue/Create.html', locals())


@csrf_exempt
def printed(request):
    """
    打印
    :param request:
    :return: 打印页view
    """
    #resList = mth.getReqVal(request, 'list', '')
    #i = 0
    #for row in resList:
        #i += 1
        #sn = row.couponno

    return render(request, 'voucher/issue/Print.html', locals())
