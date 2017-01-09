#-*- coding:utf-8 -*-
__author__ = 'qixu'
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Max
from django.core.paginator import Paginator #分页查询
import datetime, json, pymssql
from sellcard.common import Constants
from sellcard.common import Method as mth
from sellcard.models import Shops,KfJobsCoupon,KfJobsCouponSn

def index(request):
    """
       代金券核销记录controllers
       :param request:
       :return:列表view
    """
    shop = request.session.get('s_shopcode')
    today = str(datetime.date.today())
    role = request.session.get('s_roleid')
    shops = Shops.objects.values('shop_code','shop_name','city').order_by('shop_code')
    List = Shops.objects.values('shop_code')
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
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)

    code_list = []

    if shopcode != '':
        code_list.append(shops.get(shop_code=shopcode)['shop_code'])
    else:
        for item_shop in shops:
            code_list.append(item_shop['shop_code'])
    code_list = str(code_list)
    code_list = code_list.replace('[','').replace(']','')

    sql = u" SELECT c.shop_code, " \
          u" sum(CASE WHEN c.type = 1 THEN IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS card_amount, " \
          u" sum(CASE WHEN c.type = 1 THEN c.`values` * IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS card_account, " \
          u" sum(CASE WHEN c.type = 2 THEN IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS goods_amount, " \
          u" sum(CASE WHEN c.type = 2 THEN c.`values` * IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS goods_account " \
          u" FROM kf_jobs_coupon c, " \
          u" (SELECT count(cs.voucher) AS used_amount, cs.coupon_code " \
          u" FROM kf_jobs_coupon_sn cs " \
          u" WHERE cs.used_flag = 1 AND cs.used_shop IN ({shops}) " \
          u" AND cs.used_date BETWEEN '{start}' AND '{end}' " \
          u" GROUP BY cs.coupon_code ) jcs " \
          u" WHERE jcs.coupon_code = c.coupon_code " \
          u" GROUP BY c.shop_code ".format(shops=code_list, start=start, end=endTime)

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    cur.execute(sql)
    snList = cur.fetchall()
    cur.close()
    conn.close()

    ErpList = getAmount(start, endTime, code_list)

    total={}
    total['card_amount'] = 0
    total['card_account'] = 0
    total['goods_amount'] = 0
    total['goods_account'] = 0
    total['common_amount'] = 0
    total['common_account'] = 0
    total['total_amount'] = 0
    total['total_account'] = 0

    for item in List:
        item['card_amount'] = 0
        item['card_account'] = 0
        item['goods_amount'] = 0
        item['goods_account'] = 0
        item['common_amount'] = 0
        item['common_account'] = 0
        item['total_amount'] = 0
        item['total_account'] = 0
        for item_sn in snList:
            if item['shop_code'] == item_sn['shop_code']:
                item['card_amount'] = item_sn['card_amount']
                total['card_amount'] += int(item_sn['card_amount'])
                item['card_account'] = item_sn['card_account']
                total['card_account'] += float(item_sn['card_account'])
                item['goods_amount'] = item_sn['goods_amount']
                total['goods_amount'] += int(item_sn['goods_amount'])
                item['goods_account'] = item_sn['goods_account']
                total['goods_account'] += float(item_sn['goods_account'])
        for item_erp in ErpList:
            if item['shop_code'] == item_erp['shop_code']:
                item['common_amount'] = item_erp['common_amount']
                total['common_amount'] += int(item_erp['common_amount'])
                item['common_account'] = item_erp['common_account']
                total['common_account'] += float(item_erp['common_account'])
        item['total_amount'] = int(item['card_amount'])+int(item['goods_amount'])+int(item['common_amount'])
        total['total_amount'] += int(item['total_amount'])
        item['total_account'] = float(item['card_account'])+float(item['goods_account'])+float(item['common_account'])
        total['total_account'] += float(item['total_account'])
    return render(request, 'report/voucher/used/list.html', locals())


def detail(request):
    if request.method == 'POST':
        shop_code=request.POST.get('t_shop_code')
        start=request.POST.get('t_start')
        end=request.POST.get('t_end')
        shop=request.POST.get('t_shop')
        type=request.POST.get('t_type')

        shops = Shops.objects.values('shop_code', 'shop_name', 'city').order_by('shop_code')
        role = request.session.get('s_roleid')
        if role in ('1', '6', '7'):
            shops = shops
        elif role == '8':  # 承德总部财务
            shops = shops.filter(city='C')
        elif role == '9':  # 唐山总部财务
            shops = shops.filter(city='T')
        else:
            shops = shops.filter(shop_code=shop)

        code_list = []
        if shop_code != '':
            code_list.append(shops.get(shop_code=shop_code)['shop_code'])
        else:
            for item_shop in shops:
                code_list.append(item_shop['shop_code'])
        code_list = str(code_list)
        code_list = code_list.replace('[', '').replace(']', '')

        List =[]

        if type != '3':
            sql = u" SELECT c.shop_code, c.`values`, c.coupon_name, c.coupon_code, " \
                  u" c.start_date, c.end_date, c.`range`, jcs.used_amount, " \
                  u" c.`values` * jcs.used_amount AS used_account, '0' AS serial_id " \
                  u" FROM kf_jobs_coupon c, " \
                  u" (SELECT count(cs.voucher) AS used_amount, cs.coupon_code " \
                  u" FROM kf_jobs_coupon_sn cs " \
                  u" WHERE cs.used_flag = 1 " \
                  u" AND cs.used_shop IN ({code_list}) " \
                  u" AND cs.used_date BETWEEN '{start}' AND '{end}' " \
                  u" GROUP BY cs.coupon_code ) jcs " \
                  u" WHERE jcs.coupon_code = c.coupon_code " \
                  u" AND c.type = '{type}' " \
                  u" AND c.shop_code = '{shop}' ".format(code_list=code_list,
                                                        start=start,
                                                        end=end,
                                                        type=type,
                                                        shop=shop)

            conn = mth.getMysqlConn()
            cur = conn.cursor()
            cur.execute(sql)
            List = cur.fetchall()
            cur.close()
            conn.close()
        else:
            serial_id = KfJobsCouponSn.objects.exclude(serial_id='0').filter(request_shop=shop,
                                                                             used_flag=1,
                                                                             used_date__lte=start,
                                                                             used_date__gte=end,
                                                                             used_shop__in=code_list)\
                .values('coupon_code').aggregate(serial_id=Max('serial_id'))
            serial_id = str(serial_id)
            serial_id = serial_id.replace('[', '').replace(']', '')
            List = getDetail(code_list,start,end,shop,serial_id)

    return render(request, 'report/voucher/used/detail.html', locals())



def getAmount(start, end, shops):
    """
    获取已使用券数量
    :param start:开始时间
    :param end: 结束时间
    :param shops: 商店编码数组
    :return: 列表
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    cur = conn.cursor()
    sql = u"select ShopID AS shop_code, " \
          u"       count(CouponNO) AS common_amount, " \
          u"       sum(ISNULL(ClearValue,0)) AS common_account " \
          u"  from MyShop_Coupon " \
          u" where ClearFlag = 1 " \
          u"   and CouponTypeID like '8%'" \
          u"   and ClearSDate BETWEEN '{start}' AND '{end}' "\
          u"   and ClearShopID in ({shops})  "\
          u" group by ShopID ".format(start=start,
                                        end=end,
                                        shops=shops)
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list


def getDetail(used_shop, start, end, request_shop, serial_id):
    """
    获取已使用券数量
    :param used_shop:使用门店
    :param start:开始时间
    :param end: 结束时间
    :param request_shop: 发行门店
    :param serial_id: 批次号
    :return: 列表
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    cur = conn.cursor()
    sql = u" SELECT c.ShopID AS shop_code, " \
          u"         c.`Value` AS `values`, " \
          u"         ct.CouponTypeName AS coupon_name, " \
          u"         c.StartDate AS start_date, " \
          u"         c.EndDate AS end_date, " \
          u"         CASE WHEN ct.IfCurrShop = 0 THEN '全部店' " \
          u"          ELSE '发行店' END AS `range`, " \
          u"         count(c.CouponNO) AS used_amount, " \
          u"         c.`Value` * count(c.CouponNO) AS used_account," \
          u"         c.SerialID AS serial_id," \
          u"         '0' AS coupon_code " \
          u" FROM MyShop_Coupon c, " \
          u"       MyShop_CouponType ct " \
          u" WHERE c.CouponTypeID = ct.CouponTypeID " \
          u"   AND c.ClearFlag = 1 " \
          u"   AND c.ClearShopID IN ({code_list}) " \
          u"   AND c.ClearSDate BETWEEN '{start}' AND '{end}' " \
          u"   AND c.ShopID = '{shop}' " \
          u"   AND c.SerialID IN ({serial_id}) " \
          u" GROUP BY c.ShopID, " \
          u"           c.`Value`, " \
          u"           ct.CouponTypeName, " \
          u"           c.StartDate," \
          u"           c.EndDate, " \
          u"           ct.IfCurrShop," \
          u"           c.SerialID ".format(code_list=used_shop,
                                            start=start,
                                            end=end,
                                            shop=request_shop,
                                            serial_id=serial_id)
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list