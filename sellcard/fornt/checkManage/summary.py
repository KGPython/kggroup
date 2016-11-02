from django.shortcuts import render
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import datetime

from sellcard.models import Orders,AdminUser
from sellcard.common import Method as mth

@csrf_exempt
def cardSale(request):
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    user = request.session.get('s_uid')

    if role in ('1','2','6'):
        personList = AdminUser.objects.values('id','name').filter(shop_code=shop)

    today = str(datetime.date.today())
    start = mth.getReqVal(request,'start',today)
    end = mth.getReqVal(request,'end',today)
    if role in ('3','5'):
        operator = user
    if role in ('1', '2', '6'):
        operator = mth.getReqVal(request, 'operator', '')
    end2 = datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(1)

    #汇总数据
    kwargs ={}
    kwargs.setdefault('add_time__gte',start)
    kwargs.setdefault('add_time__lte',end2)
    if operator:
       kwargs.setdefault('operator_id',operator)
    dataTotal = Orders.objects.filter(**kwargs).aggregate(saleTotal=Sum('paid_amount'),discTotal=Sum('disc_amount'))

    #卡面值列表
    conn = mth.getMysqlConn()
    whereStr = 'ord.shop_code = "'+shop+'" and ord.order_sn=info.order_id and ord.add_time>= "'+str(start)+'" and ord.add_time<= "'+str(end2)+'" '
    if operator:
        whereStr += ' and operator_id = "'+str(operator)+'" '
    sqlInfo = 'select info.card_balance, count(*) as num from order_info info,orders ord ' \
              'where '+ whereStr+'group by info.card_balance'
    cur = conn.cursor()
    cur.execute(sqlInfo)
    dataInfo =cur.fetchall()

    return render(request, 'summary_cardSale.html', locals())
