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
    检验券真伪controllers
    :param request:
    :return:
    """
    if request.method == 'POST':
        batch = request.POST.get('batch', '')
        voucher = request.POST.get('voucher', '')
        result = request.POST.get('result', '')

        salts = KfJobsCouponSn.objects.values('salt'
                                              ).filter(batch=batch,
                                                       voucher=voucher)
        if salts is not None and len(salts) > 0:
            salt = salts[0]['salt']

            m = hashlib.md5()
            m.update(voucher.encode(encoding='UTF-8'))
            verifier = m.hexdigest()
            mdfive = verifier + salt
            m.update(mdfive.encode(encoding='UTF-8'))
            verifier = m.hexdigest()
            if (result == verifier):
                msg = 1
            else:
                msg = 0
        else:
            msg = 0
    return render(request, 'voucher/verifier/verifier.html', locals())
