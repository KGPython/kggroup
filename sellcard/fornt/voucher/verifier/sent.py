#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard import views as base
from django.db import transaction
import datetime,json

from sellcard.models import KfJobsCouponSn,ActionLog
from sellcard.common.model import MyError


def index(request):
    shops = base.findShop()

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token

    return render(request,'voucher/verifier/sent.html',locals())

@transaction.atomic
def save(request):
    res = {}
    if request.method == 'POST':
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            res["msg"] = 0
            return HttpResponse(json.dumps(res))

        path = request.path
        batch = request.POST.get('batch')
        start=request.POST.get('start')
        end=request.POST.get('end')
        subTotal=int(request.POST.get('subTotal'))
        shop=request.POST.get('shop')
        person=request.POST.get('person')

        try:
            with transaction.atomic():
                l = KfJobsCouponSn.objects.filter(sn__lte=end,sn__gte=start,batch=batch,state=0)
                updataNum = KfJobsCouponSn.objects.filter(sn__lte=end,sn__gte=start,batch=batch,state=0)\
                    .update(request_name = person,request_shop = shop,request_date=datetime.datetime.now(),state=1)

                if updataNum == subTotal:
                    res['msg'] = 1
                else:
                    raise MyError('数据更新失败')

                ActionLog.objects.create(url=path, u_name=request.session.get('s_uname'),
                                         cards_out=start + '--' + end, add_time=datetime.datetime.now())
                del request.session['postToken']

        except MyError as e1:
            print('My exception occurred, value:', e1.value)
            res['msg'] = 0
            res['cardId'] = e1.value
            ActionLog.objects.create(action='代金卷验证码领取', u_name=request.session.get('s_uname'), cards_out=start + '--' + end,
                                     add_time=datetime.datetime.now(), err_msg=e1.value)

        except Exception as e:
            print(e)
            res['msg'] = 0
            ActionLog.objects.create(action='代金卷验证码领取', u_name=request.session.get('s_uname'), cards_out=start + '--' + end,
                                     add_time=datetime.datetime.now(), err_msg=e)

    return HttpResponse(json.dumps(res))

