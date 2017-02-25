#-*- coding:utf-8 -*-
from django.shortcuts import render

from sellcard import views as base
import datetime,json

from sellcard.common import Method as mth
from sellcard.models import ReceiveInfo

def index(request):
    sql = "select * from order_borrow"
    if request.method == 'POST':
        pass
    return render(request, 'report/card/borrow/index.html', locals())

