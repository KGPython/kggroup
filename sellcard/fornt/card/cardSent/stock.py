# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/8/8 8:56'
import json
from django.shortcuts import render
from  django.http import  HttpResponse
from django.db import transaction
from django.db.models import F

from sellcard import views as base
from sellcard.models import CardStockIo, CardStockInside, CardStockOutside
from sellcard.common.model import MyError


@transaction.atomic
def index(request):
    if request.method == 'POST':
        operator = request.session.get('s_uid', '')
        source = request.POST.get('source', '')
        target = request.POST.get('target', '')
        res = {'status':'1'}
        if (source == 'factory' and target!='outside')  or (source == 'outside' and target!='inside') or (source == 'inside' and target.find('side')>=0):
            res['status'] = '0'
            res['msg'] = '出入库选择有误！'
            return HttpResponse(json.dumps(res))

        data = request.POST.get('list', [])
        data = json.loads(data)

        try:
            with transaction.atomic():
                io_list = []
                for item in data:
                    io = CardStockIo()
                    io.source = source
                    io.target = target
                    io.operator = operator
                    if item['type'] == '9' and item['value'] != "会员卡":
                        raise MyError('卡类型对应的卡面值有误')
                    elif item['type'] in ('1','2','3','4') and item['value'] == "会员卡":
                        raise MyError('卡类型对应的卡面值有误')

                    io.type = item['type']
                    io.value = item['value']
                    io.num = item['num']
                    io.remark = item['remark']
                    io_list.append(io)

                    if source == 'factory':
                        qs_out = CardStockOutside.objects.filter(value=item['value'],type=item['type'])
                        if qs_out.count() > 0:
                            qs_out.update(num=F('num') + int(item['num']))
                        else:
                            CardStockOutside.objects.create(
                                type=item['type'], value=item['value'], num=item['num']
                            )
                    elif source == 'outside':
                        CardStockOutside.objects.filter(value=item['value'],type=item['type'])\
                            .update(num=F('num') - int(item['num']))
                        qs_in = CardStockInside.objects.filter(value=item['value'],type=item['type'])
                        if qs_in.count() > 0:
                            qs_in.update(num=F('num') + int(item['num']))
                        else:
                            CardStockInside.objects.create(
                                type=item['type'], value=item['value'], num=item['num']
                            )
                    elif source == 'inside':
                        CardStockInside.objects.filter(value=item['value'],type=item['type'])\
                            .update(num=F('num') - int(item['num']))
                CardStockIo.objects.bulk_create(io_list)
        except Exception as e:
            res['status'] = 2
            if hasattr(e, 'value'):
                res['msg'] = e.value
            res['msg'] = '数据存储失败！'

        return HttpResponse(json.dumps(res))

    if request.method == 'GET':
        shops = base.findShop()
        cardTypes = base.findCardType()
        # 在服务端session中添加key认证，避免用户重复提交表单
        token = 'allow'  # 可以采用随机数
        request.session['postToken'] = token
        return render(request, 'card/sent/stock.html', locals())

def stockIO(request):
    inside_list = CardStockInside.objects.values().all().order_by('type','value')
    outside_list = CardStockOutside.objects.values().all().order_by('type','value')

    return render(request,'card/sent/stockIO.html',locals())

def stockLog(request):
    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')
        source = request.POST.get('source','')
        kwarg = {}
        if start:
            kwarg.setdefault('create_time__gte',start)
        if end:
            kwarg.setdefault('create_time__lte',end)
        if source:
            kwarg.setdefault('source',source)
        log_list = CardStockIo.objects.values().filter(**kwarg)
    return render(request,'card/sent/ioLog.html',locals())

