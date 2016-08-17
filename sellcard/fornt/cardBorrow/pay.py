#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json,datetime

from sellcard.models import OrderBorrow,OrderBorrowInfo,CardInventory
from sellcard.common import Method as mth

@csrf_exempt
def index(request):
    operator = request.session.get('s_uid','')
    rates = request.session.get('s_rates')
    today = str(datetime.date.today())
    start = today
    end = today
    if request.method == 'POST':
        departName = request.POST.get('departName','')
        departCode = request.POST.get('departCode','')
        state = request.POST.get('state','')
        start = request.POST.get('start','')
        end = request.POST.get('end','')

        nextDay = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)

        kwargs = {}
        kwargs.setdefault('operator',operator)
        whereStr =''
        if departName:
            whereStr +=' and borrow_depart="'+departName+'"'
            kwargs.setdefault('borrow_depart',departName)
        if departCode:
            whereStr +=' and borrow_depart_code="'+departCode+'"'
            kwargs.setdefault('borrow_depart_code',departCode)
        if state:
            whereStr +=' and stutas="'+state+'"'
            kwargs.setdefault('is_paid',state)
        if start:
            whereStr +=' and add_time>="'+str(start)+'"'
            kwargs.setdefault('add_time__gte',start)
        if end:
            whereStr +=' and add_time<="'+str(nextDay)+'"'
            kwargs.setdefault('add_time__lte',nextDay)

        #查询借卡明细
        listSale = OrderBorrow\
                .objects\
                .values('order_sn','order_val','order_num','operator','borrow_depart','borrow_depart_code','borrow_name','add_time','is_paid')\
                .filter(**kwargs).order_by('order_sn')

        totaSale = 0
        for row in listSale:
            totaSale += row['order_val']

        #查询退卡明细
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        sqlBack = 'select a.order_sn,a.operator,a.borrow_depart,a.borrow_depart_code,SUM(b.card_balance) as back_val,COUNT(b.card_no) as back_num,b.back_time' \
                  ' from order_borrow as a,order_borrow_info as b ' \
                  ' where a.order_sn=b.order_sn and b.is_back="1"'+whereStr+' group by(a.order_sn)'
        cur.execute(sqlBack)
        listBack = cur.fetchall()

        totalBack = 0
        for row2 in listBack:
            totalBack += row2['back_val']
        #退卡后应缴费用
        totalPay = totaSale-totalBack

        #查询未退卡明细
        sqlCardNoBack = 'select b.card_no as cardId,b.card_balance as cardVal from order_borrow as a,order_borrow_info as b ' \
                  ' where a.order_sn=b.order_sn and b.is_back is null '+whereStr+''
        cur.execute(sqlCardNoBack)
        listNoBack = cur.fetchall()
        for item in listNoBack:
            item['cardVal'] = str(item['cardVal'])

        cur.close()
        conn.close()
    return render(request,'borrowPay.html',locals())


def save(request):
    pass