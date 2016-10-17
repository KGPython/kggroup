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
    shops = base.findShop()
    departs = base.findDepart()
    today = str(datetime.date.today())

    resList=[]
    #判断用户角色
    if role_id=='2':
        shop = shopcode
    if role_id =='1' or role_id=='6':
        shop = mth.getReqVal(request,'shop','')
        actionType = mth.getReqVal(request,'actionType','1')
    depart = mth.getReqVal(request,'depart','')
    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    endTime = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request,'page',1)

    name = mth.getReqVal(request,'operator','').strip()
    operator =''
    if name:
        user = AdminUser.objects.values('id').filter(name=name)
        if not user:
            return  render(request,'saleQuery.html',locals())
        else:
            operator = user[0]['id']
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
    return  render(request,'saleQuery.html',locals())

