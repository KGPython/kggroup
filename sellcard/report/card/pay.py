# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/10/12 13:44'
import datetime

from django.shortcuts import render
from sellcard.models import OrderPaymentCredit

from sellcard.common import Method as mth

def bank_paid(request):
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        list = OrderPaymentCredit.objects.defer('remarks','create_time','create_user_id','create_user_name')\
            .filter(create_time__gte=start,create_time__lte=end,pay_id=3,pay_id_old__in=[3,4])
    if request.method == 'GET':
        pass
    return render(request, 'report/card/pay_bank.html', locals())


