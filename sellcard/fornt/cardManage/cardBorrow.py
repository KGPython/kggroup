#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json,datetime

from sellcard import views as base
from sellcard.common import Method as mth
from sellcard.models import OrderBorrow,OrderBorrowInfo

@csrf_exempt
def index(request):
    return render(request,'cardBorrow.html',locals())
