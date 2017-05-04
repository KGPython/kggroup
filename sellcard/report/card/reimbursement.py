# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import OrderUpCard, Payment
from sellcard.common import Method as mth
from sellcard import views as base


def index(request):
    shop = request.session.get('s_shopcode', '')
    role_id = request.session.get('s_roleid')
    if request.method == 'GET':
        start = str(datetime.date.today().replace(day=1))
        end = str(datetime.date.today())
        endTime = str(datetime.date.today() + datetime.timedelta(1))
    if request.method == 'POST':
        today = datetime.date.today()
        start = request.POST.get('start', today)
        end = request.POST.get('end', today)
        endTime = str(datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1))

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    if role_id == '1' or role_id == '6':
        shops = mth.getCityShops()
        shopsCode = mth.getCityShopsCode()
    if role_id == '9':
        shops = mth.getCityShops('T')
        shopsCode = mth.getCityShopsCode('T')
    if role_id == '8':
        shops = mth.getCityShops('C')
        shopsCode = mth.getCityShopsCode('C')
    if role_id == '10' or role_id == '2':
        shops = base.findShop(shop)
        shopsCode = [shop]

    shopsCodeStr = "'" + "','".join(shopsCode) + "'"
