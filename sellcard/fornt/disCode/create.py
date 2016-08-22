#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from random import sample
from sellcard.models import DisCode
# str = ''.join(sample('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789', 8))

@csrf_exempt
def index(request):
    if request.method == 'POST':
        prefix = request.POST.get('prefix')
        for i in range(0,99999):
            disCode = ''.join(sample('abcdefghijklmnopqrstuvwxyz0123456789', 8))
            obj = DisCode()
            obj.dis_code = prefix+disCode
            obj.save()

    return render(request,'disCodeCreate.html',locals())
