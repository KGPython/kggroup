#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard import views as base
from django.db import transaction
import datetime,json

from sellcard.common import Method as mth
from sellcard.models import KfJobsCouponSn
from sellcard.common.model import MyError

def index(request):
    shops = base.findShop()
    return render(request,'voucher/verifier/sent.html')