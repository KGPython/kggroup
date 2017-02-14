# -*-  coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard.models import OrderErr
import json,datetime
import sellcard.views as base

def create(request):
    u_id = request.session.get('s_uid')
    shop = request.session.get('s_shopcode')
    sn = request.POST.get('orderSn')
    record = request.POST.get('payJsonStr')
    today = datetime.date.today()
    data = OrderErr.objects.create(u_id=u_id, order_sn=sn, record=record, c_time=today, shop=shop,type='1')
    data_id = data.id
    res = {}
    if data_id:
        res['msg'] = 0
    else:
        res['msg'] = 1
    return HttpResponse(json.dumps(res))


def index2(request):
    shops = base.findShop()
    monthFirst = str(datetime.date.today().replace(day=1))
    now = str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'GET':
        start = monthFirst
        end = now
    if request.method == 'POST':
        start = request.POST.get('start',monthFirst)
        end = request.POST.get('end',now)
        shop = request.POST.get('shop','C001')
        errs = OrderErr.objects.values('record','c_time','u_id','shop','c_time')\
               .filter(c_time__gte=start,c_time__lte=end).order_by('shop','c_time')

        total = {}
        data = []
        for err in errs:
            records = json.loads(err['record'])
            row = {}
            row['shop'] = err['shop']
            row['c_time'] = err['c_time']
            for record in records:
                if record['payOld'] in row:
                    row[record['payOld']] += -float(record['payVal'])
                else:
                    row[record['payOld']] = -float(record['payVal'])
                if record['payNew'] in row:
                    row[record['payNew']] += float(record['payVal'])
                else:
                    row[record['payNew']] = float(record['payVal'])
                #合计
                if record['payOld'] in total:
                    total[record['payOld']] += -float(record['payVal'])
                else:
                    total[record['payOld']] = -float(record['payVal'])
                if record['payNew'] in total:
                    total[record['payNew']] += float(record['payVal'])
                else:
                    total[record['payNew']] = float(record['payVal'])
            data.append(row)
    return render(request,'report/card/orderAdjust/index.html',locals())

def index(request):
    shops = base.findShop()
    monthFirst = str(datetime.date.today().replace(day=1))
    now = str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'GET':
        start = monthFirst
        end = now
    if request.method == 'POST':
        start = request.POST.get('start',monthFirst)
        end = request.POST.get('end',now)
        shop = request.POST.get('shop','C001')
        errs = OrderErr.objects.values('record','c_time','u_id','shop','c_time')\
               .filter(c_time__gte=start,c_time__lte=end).order_by('shop','c_time')

        total = {}
        data = []
        #订单数据列传行
        for err in errs:
            records = json.loads(err['record'])
            row = {}
            row['shop'] = err['shop']
            row['c_time'] = err['c_time']
            for record in records:
                if record['payOld'] in row:
                    row[record['payOld']] += -float(record['payVal'])
                else:
                    row[record['payOld']] = -float(record['payVal'])
                if record['payNew'] in row:
                    row[record['payNew']] += float(record['payVal'])
                else:
                    row[record['payNew']] = float(record['payVal'])
                #合计
                if record['payOld'] in total:
                    total[record['payOld']] += -float(record['payVal'])
                else:
                    total[record['payOld']] = -float(record['payVal'])
                if record['payNew'] in total:
                    total[record['payNew']] += float(record['payVal'])
                else:
                    total[record['payNew']] = float(record['payVal'])
            data.append(row)
        #以日为单位，汇总
        for row in data:
            shop = row['shop']
            date = row['c_time']
            for row2 in data :
                if row2['shop'] == shop and row2['c_time'] == date and row!=row2:
                    for key in row2.keys():
                        if (key in row.keys()) and (key not in ('shop','c_time')):
                            row[key] += float(row2[key])
                        else:
                            row[key] = row2[key]
                    data.remove(row2)

    return render(request,'report/card/orderAdjust/index.html',locals())
