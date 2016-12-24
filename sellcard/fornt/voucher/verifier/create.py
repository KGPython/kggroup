# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
import datetime, hashlib
from random import sample
from sellcard.models import KfJobsCouponSn


@transaction.atomic
def index(request):
    """
    生成验证码controllers
    :param request:
    :return:
    """
    if request.method == 'POST':
        amount = request.POST.get('amount', '')
        year = datetime.datetime.now().strftime('%y')

        batchs = KfJobsCouponSn.objects.values('batch'
                                               ).filter(batch__startswith=year)
        batch = batchs.aggregate(Max('batch'))

        if batch['batch__max'] is None:
            batch = 1
        else:
            batch = int(batch['batch__max'][2:]) + 1
        batch = year + str(batch)

        List = set()
        while len(List) < int(amount):
            var_sn = batch + ''.join(sample('0123456789', 10))
            List.add(var_sn)
        n = 0
        for voucher in List:
            n = n + 1
            sn = str(n).zfill(6)
            salt = ''.join(sample('0123456789abcdefghijklmnopqrstuvwxyz', 16))
            m = hashlib.md5()
            m.update(voucher.encode(encoding='UTF-8'))
            result = m.hexdigest()
            mdfive = result + salt
            m.update(mdfive.encode(encoding='UTF-8'))
            result = m.hexdigest()
            KfJobsCouponSn.objects.create(sn=sn,
                                          batch=batch,
                                          voucher=voucher,
                                          salt=salt,
                                          result=result)
        msg = 1
    return render(request, 'voucher/verifier/create.html', locals())
