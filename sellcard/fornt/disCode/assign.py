#-*- coding:utf-8 -*-
from django.shortcuts import render
from random import sample
from sellcard.models import DisCode

def index(request):
    prefix = request.POST.get('prefix')
    for i in range(0,999999999):
        str = prefix.join(sample('0123456789', 10))
        obj = DisCode()
        obj.dis_code = str
        obj.save()

    return render(request,'disCodeCreate.html',locals())
