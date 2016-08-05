#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sellcard import views as base


@csrf_exempt
def index(request):
    shops = base.findShop()
    cardTypes = base.findCardType()
    return render(request,'cardAllocation.html',locals())