#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import datetime,time

from sellcard.common import Method as mth
from sellcard import views as base
from sellcard.models import Orders,AdminUser,OrderUpCard,OrderChangeCard


@csrf_exempt
def index(request):
    #GET:数据展示
    role_id = request.session.get('s_roleid')
    shopcode = request.session.get('s_shopcode')
    depart_id = request.session.get('s_depart')
    user_id = request.session.get('s_uid') #当前用户ID
    shops = base.findShop()
    departs = base.findDepart()
    today = str(datetime.date.today())

    resList=[]
    #判断用户角色
    shop = ''
    operator = ''
    if role_id in ('1','6'):
        shop = mth.getReqVal(request,'shop','')
        depart = mth.getReqVal(request, 'depart', '')
        name = mth.getReqVal(request, 'operator', '').strip()
        if name:
            user = AdminUser.objects.values('id').filter(name=name)
            if not user:
                return render(request, 'report/saleGroupByOrder.html', locals())
            else:
                operator = user[0]['id']
    if  role_id == '2':
        shop = shopcode
        depart = mth.getReqVal(request, 'depart', '')
        name = mth.getReqVal(request, 'operator', '').strip()
        if name:
            user = AdminUser.objects.values('id').filter(name=name)
            if not user:
                return render(request, 'report/saleGroupByOrder.html', locals())
            else:
                operator = user[0]['id']

    if role_id in ('3','5'):
        shop = shopcode
        depart = depart_id
        operator = user_id
    actionType = mth.getReqVal(request,'actionType','1')

    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    endTime = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request,'page',1)


    kwargs = {}
    if shop:
        kwargs.setdefault('shop_code',shop)
    if operator:
        kwargs.setdefault('operator_id',operator)
    if depart:
        kwargs.setdefault('depart',depart)
    kwargs.setdefault('add_time__gte',start)
    kwargs.setdefault('add_time__lte',endTime)
    if actionType=='1':
        resList = Orders.objects.values('shop_code','depart','operator_id','order_sn','action_type','paid_amount','disc_amount','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')
        paidTotal = 0.00
        discTotal = 0.00
        cardCount = 0
        for item in resList:
            paidTotal += float(item['paid_amount'])
            discTotal += float(item['disc_amount'])
            cardCount +=1
    elif actionType=='2':
        resList = OrderUpCard.objects.values('shop_code','depart','operator_id','order_sn','diff_price','user_name','user_phone','modified_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')
    elif actionType=='3':
        resList = OrderChangeCard.objects.values('shop_code','depart','operator_id','order_sn','total_in_price','total_out_price','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')

    paginator = Paginator(resList,20)
    try:
        resList = paginator.page(page)
    except Exception as e:
        print(e)
    return  render(request, 'report/saleGroupByOrder.html', locals())

