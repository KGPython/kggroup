# -*-  coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from sellcard.models import OrderErr
import json,datetime
import sellcard.views as base
from sellcard.common import Method as mth
def create(request):
    role = request.session.get('s_roleid')
    u_id = request.session.get('s_uid')

    if role not in ('1','6'):
        shop = request.session.get('s_shopcode')
    else:
        shop = request.POST.get('shop')
    sn = request.POST.get('orderSn')
    record = request.POST.get('payJsonStr')
    today = datetime.date.today()
    res = {}
    try:
        qs_err = OrderErr.objects.select_for_update().filter(order_sn=sn)
        if qs_err.count()>0:
            qs_err.update(u_id=u_id,record=record, c_time=today, shop=shop,type='1')
        else:
            OrderErr.objects.create(u_id=u_id,record=record, c_time=today, shop=shop,type='1',order_sn=sn)
        res['msg'] = 0
    except Exception as e:
        print(e)
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
    u_role = request.session.get('s_roleid')

    if u_role == '1' or u_role == '6':
        shops = mth.getCityShops()
    if u_role == '9':
        shops = mth.getCityShops('T')
    if u_role == '8':
        shops = mth.getCityShops('C')
    if u_role == '10' or u_role == '2':
        u_shop = request.session.get('s_shopcode')

    monthFirst = str(datetime.date.today().replace(day=1))
    now = str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'GET':
        start = monthFirst
        end = now
    if request.method == 'POST':
        start = request.POST.get('start',monthFirst)
        end = request.POST.get('end',now)
        shop = request.POST.get('shop','')
        kwargs = {}
        kwargs.setdefault('c_time__gte',start)
        kwargs.setdefault('c_time__lte',end)
        if shop:
            kwargs.setdefault('shop', shop)
        errs = OrderErr.objects.values('record','c_time','u_id','shop','c_time')\
               .filter(**kwargs).order_by('shop','c_time')

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
            row_shop = row['shop']
            date = row['c_time']
            for row2 in data :
                if row2['shop'] == row_shop and row2['c_time'] == date and row!=row2:
                    for key in row2.keys():
                        if (key in row.keys()) and (key not in ('shop','c_time')):
                            row[key] += float(row2[key])
                        else:
                            row[key] = row2[key]
                    data.remove(row2)

    return render(request,'report/card/orderAdjust/index.html',locals())
