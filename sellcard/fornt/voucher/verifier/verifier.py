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

        get_info = KfJobsCouponSn.objects.values('salt', 'sn'
                                                 ).filter(batch=batch,
                                                          voucher=voucher)
        if get_info is not None and len(get_info) > 0:
            salt = get_info[0]['salt']
            sn = get_info[0]['sn']

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
            verifier = m.hexdigest()

            if (result == verifier):
                msg = 1
            else:
                msg = 0
        else:
            msg = 0
    return render(request, 'voucher/verifier/verifier.html', locals())
