# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/8/19 9:48'
import datetime

from django.shortcuts import render

from sellcard.models import Orders
from sellcard.common import Method as mth


def bestowed(request):
    s_shop = request.session.get('s_shopcode')
    s_role = request.session.get('s_roleid')
    s_user = request.session.get('s_uid')
    if s_role in ('1', '6'):
        shops = mth.getCityShopsCode()
    elif s_role == '9':
        shops = mth.getCityShopsCode('T')
    elif s_role == '8':
        shops = mth.getCityShopsCode('C')
    elif s_role in ('2', '10'):
        shop = s_shop
    if request.method == 'POST':
        today = str(datetime.date.today())
        start = request.POST.get('start', today)
        end = request.POST.get('end', today)
        end2 = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)

        shop= ''
        if s_role in ('1', '6', '8', '9'):
            shop = request.POST.get('shop', '')
        elif s_role in ('2', '10'):
            shop = s_shop
        elif s_role in ('3', '5'):
            shop = s_shop

        kwargs = {}
        kwargs.setdefault('add_time__gte', start)
        kwargs.setdefault('add_time__lte', end2)
        kwargs.setdefault('action_type', '5')
        if shop:
            kwargs.setdefault('shop_code', shop)

        disc_list = Orders.objects.values('disc_amount','shop_code','operator_id','add_time','remark').filter(**kwargs)
        disc_total = 0
        for disc in disc_list:
            disc_total += float(disc['disc_amount'])
    if request.method == 'GET':
        pass
    return render(request, 'report/card/disc/bestowed.html', locals())