# -*-  coding:utf-8 -*-
__anthor__ = ''
__date__ = '2017/3/21 14:50'
from django.shortcuts import render


def index(request):
    if request.method == 'POST':
        pass
    return render(request, '', locals())