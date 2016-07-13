#-*- coding:utf-8 -*-
from django.shortcuts import render
from sellcard.models import Orders,OrderInfo,OrderPaymentInfo
def index(reauest):
    list = Orders.objects.all()
    return render(reauest,'cardSale.html',locals())