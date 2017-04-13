# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/4/1 16:25'
from django.http import HttpResponse

import json


def postTokenCheck(func):
    def wrapper(request):
        Token = request.session.get('postToken', default=None)
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            res = {}
            res["status"] = 0
            res['msg'] = '表单重复提交，刷新页面后，重试！'
            return HttpResponse(json.dumps(res))
        return func(request)
    return wrapper



