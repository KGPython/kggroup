#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,Count

from sellcard.models import Orders,OrderPaymentInfo
@csrf_exempt
def index(request):
    pass
