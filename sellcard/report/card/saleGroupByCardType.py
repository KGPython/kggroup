from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import Orders,AdminUser
from sellcard.common import Method as mth

def index(request):
    s_shop = request.session.get('s_shopcode')
    s_role = request.session.get('s_roleid')
    s_user = request.session.get('s_uid')
    today = str(datetime.date.today())

    shops = []
    shopsCodeStr = ''
    personList = AdminUser.objects.values('id', 'name','is_enable').filter(role_id__in=('2', '3', '5','11'))
    if s_role in ('1', '6'):
        shops = mth.getCityShopsCode()
        shopsCodeStr = "'" + "','".join(shops) + "'"
        personList = personList.filter(shop_code__in=shops)
    elif s_role == '9':
        shops = mth.getCityShopsCode('T')
        shopsCodeStr = "'" + "','".join(shops) + "'"
        personList = personList.filter(shop_code__in=shops)
    elif s_role == '8':
        shops = mth.getCityShopsCode('C')
        shopsCodeStr = "'" + "','".join(shops) + "'"
        personList = personList.filter(shop_code__in=shops)
    elif s_role in ('2', '10'):
        shop = s_shop
        personList = personList.filter(shop_code=shop)

    personList = sorted(personList, key=lambda p: p["name"].encode('gb2312'))

    if request.method == 'POST':
        shop,operator = '',''
        if s_role in ('1', '6', '8', '9'):
            shop = mth.getReqVal(request, 'shop', '')
            operator = mth.getReqVal(request, 'operator', '')
        elif s_role in ('2', '10'):
            shop = s_shop
            operator = mth.getReqVal(request, 'operator', '')
        elif s_role in ('3', '5'):
            operator = s_user
            shop = s_shop
        start = mth.getReqVal(request, 'start', today)
        end = mth.getReqVal(request,'end',today)
        end2 = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)

        #汇总数据
        kwargs ={}
        kwargs.setdefault('add_time__gte',start)
        kwargs.setdefault('add_time__lte',end2)
        if shop:
            kwargs.setdefault('shop_code',shop)
        if operator:
           kwargs.setdefault('operator_id',operator)
        if len(shops)>0:
            kwargs.setdefault('shop_code__in', shops)
        dataTotal = Orders.objects.filter(**kwargs).aggregate(saleTotal=Sum('paid_amount'),discTotal=Sum('disc_amount'))

        #卡面值列表
        conn = mth.getMysqlConn()
        whereStr = 'ord.order_sn=info.order_id and ord.add_time>= "'+str(start)+'" and ord.add_time<= "'+str(end2)+'" '
        if operator:
            whereStr += ' and operator_id = "'+str(operator)+'" '
        if shop:
            whereStr += ' and ord.shop_code = "'+shop+'"'
        if shopsCodeStr:
            whereStr += ' and ord.shop_code IN (' + shopsCodeStr + ')'
        sqlInfo = 'select ord.shop_code,info.card_balance, count(*) as num from order_info as info,orders as ord ' \
                  'where '+ whereStr+' group by ord.shop_code,info.card_balance'
        cur = conn.cursor()
        cur.execute(sqlInfo)
        dataInfo =cur.fetchall()

    return render(request, 'report/card/saleGroupByCardType.html', locals())
