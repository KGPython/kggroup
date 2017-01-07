#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.shortcuts import render
from django.db.models import Count,Sum
from django.core.paginator import Paginator #分页查询
import datetime, pymssql
from sellcard.common import Constants
from sellcard.common import Method as mth
from sellcard.models import Shops,KfJobsCoupon,KfJobsCouponSn

def index(request):
    """
       代金券库存盘点列表controllers
       :param request:
       :return:列表view
    """
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    shops = Shops.objects.values('shop_code','shop_name','city').order_by('shop_code')
    if role in ('1','6','7') :
        shops = shops
    elif role == '8':#承德总部财务
        shops = shops.filter(city='C')
    elif role == '9':#唐山总部财务
        shops = shops.filter(city='T')
    else:
        shops = shops.filter(shop_code=shop)
    shops_len = len(shops)
    shopcode = mth.getReqVal(request, 'shopcode', '')
    today = str(datetime.date.today())
    couponType = mth.getReqVal(request, 'couponType', '')
    batch = mth.getReqVal(request, 'batch', '').strip()
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request, 'page', 1)

    kwargs = {}
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

    List = KfJobsCoupon.objects.values(
        'shop_code', 'create_user_name', 'type', 'batch', 'start_date', 'values', 'coupon_code',
        'amount', 'end_date', 'discount', 'range').filter(**kwargs).order_by('create_date')

    snList = KfJobsCouponSn.objects.exclude(coupon_code='').filter(used_flag=1).values('coupon_code','serial_id').annotate(used_amount=Count('voucher'))

    ErpList = []
    if couponType == '3' or couponType == '':
        ErpList = getAmount()

    for item in List:
        item['used_amount'] = 0
        item['surplus_amount'] = item['amount']
        for sn_item in snList:
            if item['coupon_code'] == sn_item['coupon_code']:
                if item['type'] != 3:
                    item['used_amount'] = sn_item['used_amount']
                    item['surplus_amount'] = int(item['amount']) - int(sn_item['used_amount'])
                else:
                    for erp_item in ErpList:
                        if sn_item['serial_id'] == erp_item['serial_id']:
                            item['used_amount'] = erp_item['used_amount']
                            item['surplus_amount'] = int(item['amount']) - int(erp_item['used_amount'])

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
    return render(request, 'report/voucher/StockList.html', locals())


def getAmount():
    """
    获取已使用券数量
    :return:列表
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    cur = conn.cursor()
    sql = u"select SerialID as serial_id, " \
          u"       count(CouponNO) as used_amount " \
          u"  from MyShop_Coupon " \
          u" where ClearFlag = 1" \
          u"   and CouponTypeID like '8%'" \
          u" group by SerialID"
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list