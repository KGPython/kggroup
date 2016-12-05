from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import Orders,AdminUser
from sellcard.common import Method as mth
from sellcard import views as base

def index(request):
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    user = request.session.get('s_uid')
    shops = base.findShop()

    today = str(datetime.date.today())
    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    if role in ('3','5'):
        operator = user

    if role in ('1', '2', '6'):
        operator = mth.getReqVal(request, 'operator', '')


    if role in ('1','6'):
        shop = mth.getReqVal(request, 'shop', '')
        personList = AdminUser.objects.values('id', 'name')
    if role in ('2','3','5'):
        shop = shop
        personList = AdminUser.objects.values('id', 'name').filter(shop_code=shop)
    end2 = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)

    #汇总数据
    kwargs ={}
    kwargs.setdefault('add_time__gte',start)
    kwargs.setdefault('add_time__lte',end2)
    if shop:
        kwargs.setdefault('shop_code',shop)
    if operator:
       kwargs.setdefault('operator_id',operator)
    dataTotal = Orders.objects.filter(**kwargs).aggregate(saleTotal=Sum('paid_amount'),discTotal=Sum('disc_amount'))

    #卡面值列表
    conn = mth.getMysqlConn()
    whereStr = 'ord.order_sn=info.order_id and ord.add_time>= "'+str(start)+'" and ord.add_time<= "'+str(end2)+'" '
    if operator:
        whereStr += ' and operator_id = "'+str(operator)+'" '
    if shop:
        whereStr += ' and ord.shop_code = "'+shop+'"'

    sqlInfo = 'select ord.shop_code,info.card_balance, count(*) as num from order_info as info,orders as ord ' \
              'where '+ whereStr+' group by ord.shop_code,info.card_balance'
    cur = conn.cursor()
    cur.execute(sqlInfo)
    dataInfo =cur.fetchall()

    return render(request, 'report/saleGroupByCardType.html', locals())
