#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.shortcuts import render
from django.db.models import Sum,Count
from django.core.paginator import Paginator #分页查询
import datetime

from sellcard.models import CardInventory,Shops
from sellcard.common import Method as mth

def index(request):
    shopCode = mth.getReqVal(request,'shopcode','')
    cardType = mth.getReqVal(request,'cardtype','')
    page = mth.getReqVal(request,'page',1)



    return render(request, 'report/stockGroupByCardNo.html', locals())
