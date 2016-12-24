# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
import datetime, hashlib, random
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

        chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',]

        List = set()
        while len(List) < int(amount):
            y = [y for y in [random.randint(x - x, len(chars) - 1) for x in range(10)]]
            charlist = [chars[i] for i in y]
            var_sn = batch + ''.join(map(str, charlist))
            List.add(var_sn)
        n = 0
        for voucher in List:
            n = n + 1
            sn = str(n).zfill(6)
            y = [y for y in [random.randint(x - x, len(chars) - 1) for x in range(16)]]
            charlist = [chars[i] for i in y]
            salt = ''.join(map(str, charlist))
            m = hashlib.md5()
            m.update(voucher.encode(encoding='UTF-8'))
            mdfive_vou = m.hexdigest()
            m.update(sn.encode(encoding='UTF-8'))
            mdfive_sn = m.hexdigest()
            m.update(salt.encode(encoding='UTF-8'))
            mdfive_salt = m.hexdigest()
            mdfive = mdfive_vou + mdfive_sn
            m.update(mdfive.encode(encoding='UTF-8'))
            mdfive = m.hexdigest()
            mdfive = mdfive + mdfive_salt
            m.update(mdfive.encode(encoding='UTF-8'))
            result = m.hexdigest()
            KfJobsCouponSn.objects.create(sn=sn,
                                          batch=batch,
                                          voucher=voucher,
                                          salt=salt,
                                          result=result,
                                          state=0)
        msg = 1
    return render(request, 'voucher/verifier/create.html', locals())
