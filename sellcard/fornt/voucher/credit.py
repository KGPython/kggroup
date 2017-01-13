# -*- coding:utf-8 -*-
__author__ = 'qixu'
import datetime,json

from django.core.paginator import Paginator #分页查询
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render

from sellcard.common import Method as mth
from sellcard.common.model import MyError
from sellcard.models import KfJobsCoupon, KfJobsCouponCredit



def index(request):
    """
    赊销金券列表controllers
    :param request:
    :return:列表view
    """
    shop = request.session.get('s_shopcode')
    shopcode = mth.getReqVal(request, 'shopcode', '')
    today = str(datetime.date.today())
    couponType = mth.getReqVal(request, 'couponType', '')
    batch = mth.getReqVal(request, 'batch', '').strip()
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request, 'page', 1)

    kwargs = {}
    kwargs.setdefault('payment_type', 4)
    if shopcode != '':
        kwargs.setdefault('shop_code', shopcode)

    if couponType != '':
        kwargs.setdefault('type', couponType)

    if batch != '':
        kwargs.setdefault('batch', batch)

    if start != '':
        kwargs.setdefault('start_date__gte', start)

    if end != '':
        kwargs.setdefault('start_date__lte', endTime)

    List = KfJobsCoupon.objects.values('shop_code', 'coupon_code', 'create_user_name',
         'type', 'batch', 'start_date', 'end_date', 'values', 'range', 'pay_account',
          'credit_account').filter(**kwargs).order_by('create_date')

    # 表单分页开始
    paginator = Paginator(List, 8)

    try:
        List = paginator.page(page)

        if List.number > 1:
            page_up = List.previous_page_number
        else:
            page_up = 1

        if List.number < List.paginator.num_pages:
            page_down = List.next_page_number
        else:
            page_down = List.paginator.num_pages

    except Exception as e:
        print(e)
        # 表单分页结束

    return render(request,'voucher/credit/List.html',locals())

def create(request):
    """
    赊销金券列表controllers
    :param request:
    :return:列表view
    """
    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    coupon_code = mth.getReqVal(request, 'coupon_code', '')
    coupon_info = KfJobsCoupon.objects.values('pay_account', 'credit_account').get(coupon_code=coupon_code)
    receivable = float(coupon_info['pay_account']) - float(coupon_info['credit_account'])
    return render(request,'voucher/credit/create.html',locals())

def createSave(request):
    """
    赊销金券列表controllers
    :param request:
    :return:列表view
    """
    res = {}
    if request.method == 'POST':
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            res["msg"] = 0
            return HttpResponse(json.dumps(res))

        create_uesr_id = request.session.get("s_uid")
        create_user_name = request.session.get("s_unameChinese")
        coupon_code = request.POST.get('coupon_code')
        payment_type = request.POST.get('payment_type')
        pay_account = request.POST.get('pay_account')

        try:
            with transaction.atomic():
                updataNum = KfJobsCoupon.objects.filter(payment_type=4, coupon_code=coupon_code)\
                    .update(credit_account = F('credit_account') + pay_account)

                if updataNum != 1:
                    raise MyError('修改代金券批次表失败！')

                createNum = KfJobsCouponCredit.objects.create(coupon_code=coupon_code,
                                                              payment_type=payment_type,
                                                              pay_account=pay_account,
                                                              create_uesr_id=create_uesr_id,
                                                              create_user_name=create_user_name,
                                                              create_date=datetime.datetime.now())
                if createNum != 1:
                    raise MyError('新增赊销代金券明细记录失败！')

        except MyError as my_e:
            print('My exception occurred, value:', my_e.value)
            res['msg'] = 0

        except Exception as e:
            print(e)
            res['msg'] = 0

        res['msg'] = 1
        del request.session['postToken']
    return HttpResponse(json.dumps(res))