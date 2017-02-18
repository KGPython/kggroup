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
       购物券核销记录controllers
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
    start = mth.getReqVal(request, 'start', str(datetime.date.today().replace(day=1)))
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)

    code_list = []

    if shopcode != '':
        if role in ('1','6','7','8','9'):
            code_list.append(shops.get(shop_code=shopcode)['shop_code'])
        else:
            code_list.append(shops.get(shop_code=shop)['shop_code'])

    else:
        for item_shop in shops:
            code_list.append(item_shop['shop_code'])
    code_list = str(code_list)
    code_list = code_list.replace('[','').replace(']','')

    sql = u" SELECT c.shop_code, " \
          u" sum(CASE WHEN c.type = 1 THEN IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS card_amount, " \
          u" sum(CASE WHEN c.type = 1 THEN c.`values` * IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS card_account, " \
          u" sum(CASE WHEN c.type = 2 THEN IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS goods_amount, " \
          u" sum(CASE WHEN c.type = 2 THEN c.`values` * IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS goods_account, " \
          u" sum(CASE WHEN c.type = 3 THEN IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS back_amount, " \
          u" sum(CASE WHEN c.type = 3 THEN c.`values` * IFNULL(jcs.used_amount, 0) ELSE 0 END ) AS back_account " \
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

    ErpList = getAmount(start, end, code_list)

    total={}
    total['card_amount'] = 0
    total['card_account'] = 0
    total['goods_amount'] = 0
    total['goods_account'] = 0
    total['back_amount'] = 0
    total['back_account'] = 0
    total['front_amount'] = 0
    total['front_account'] = 0
    total['common_amount'] = 0
    total['common_account'] = 0
    total['total_b_amount'] = 0
    total['total_b_account'] = 0
    total['total_f_amount'] = 0
    total['total_f_account'] = 0
    total['total_amount'] = 0
    total['total_account'] = 0

    for item in List:
        item['card_amount'] = 0
        item['card_account'] = 0
        item['goods_amount'] = 0
        item['goods_account'] = 0
        item['back_amount'] = 0
        item['back_account'] = 0
        item['front_amount'] = 0
        item['front_account'] = 0
        item['common_amount'] = 0
        item['common_account'] = 0
        item['total_b_amount'] = 0
        item['total_b_account'] = 0
        item['total_f_amount'] = 0
        item['total_f_account'] = 0
        item['total_amount'] = 0
        item['total_account'] = 0
        for item_sn in snList:
            if item['shop_code'] == item_sn['shop_code']:
                item['card_amount'] = item_sn['card_amount']
                total['card_amount'] += int(item_sn['card_amount'])
                item['card_account'] = item_sn['card_account']
                total['card_account'] += float('%.2f' % item_sn['card_account'])
                item['goods_amount'] = item_sn['goods_amount']
                total['goods_amount'] += int(item_sn['goods_amount'])
                item['goods_account'] = item_sn['goods_account']
                total['goods_account'] += float('%.2f' % item_sn['goods_account'])
                item['back_amount'] = item_sn['back_amount']
                total['back_amount'] += int(item_sn['back_amount'])
                item['back_account'] = item_sn['back_account']
                total['back_account'] += float('%.2f' % item_sn['back_account'])
        for item_erp in ErpList:
            if item['shop_code'] == item_erp['shop_code']:
                item['common_amount'] = item_erp['common_amount']
                total['common_amount'] += int(item_erp['common_amount'])
                item['common_account'] = item_erp['common_account']
                total['common_account'] += float('%.2f' % item_erp['common_account'])
        item['front_amount'] = int(item['common_amount'])-int(item['back_amount'])
        total['front_amount'] += int(item['front_amount'])
        item['front_account'] = float('%.2f' % item['common_account'])-float('%.2f' % item['back_account'])
        total['front_account'] += float('%.2f' % item['front_account'])
        item['total_b_amount'] = int(item['card_amount'])+int(item['back_amount'])
        total['total_b_amount'] += int(item['total_b_amount'])
        item['total_b_account'] = float('%.2f' % item['card_account'])+float('%.2f' % item['back_account'])
        total['total_b_account'] += float('%.2f' % item['total_b_account'])
        item['total_f_amount'] = int(item['goods_amount'])+int(item['front_amount'])
        total['total_f_amount'] += int(item['total_f_amount'])
        item['total_f_account'] = float('%.2f' % item['goods_account'])+float('%.2f' % item['front_account'])
        total['total_f_account'] += float('%.2f' % item['total_f_account'])
        item['total_amount'] = int(item['card_amount'])+int(item['goods_amount'])+int(item['common_amount'])
        total['total_amount'] += int(item['total_amount'])
        item['total_account'] = float('%.2f' % item['card_account'])+float('%.2f' % item['goods_account'])+float('%.2f' % item['common_account'])
        total['total_account'] += float('%.2f' % item['total_account'])
    total['card_account'] = '%.2f' % total['card_account']
    total['goods_account'] = '%.2f' % total['goods_account']
    total['back_account'] = '%.2f' % total['back_account']
    total['front_account'] = '%.2f' % total['front_account']
    total['common_account'] = '%.2f' % total['common_account']
    total['total_b_account'] = '%.2f' % total['total_b_account']
    total['total_f_account'] = '%.2f' % total['total_f_account']
    total['total_account'] = '%.2f' % total['total_account']
    return render(request, 'report/voucher/used/list.html', locals())


def detail(request):
    if request.method == 'POST':
        page = mth.getReqVal(request, 'page', 1)
        shop_code=request.POST.get('t_shop_code')
        shop=request.POST.get('t_shop')
        type=request.POST.get('t_type')
        start=request.POST.get('t_start')
        end=request.POST.get('t_end')
        endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)

        shops = Shops.objects.values('shop_code', 'shop_name', 'city').order_by('shop_code')
        role = request.session.get('s_roleid')
        if role in ('1', '6', '7'):
            shops = shops
        elif role == '8':  # 承德总部财务
            shops = shops.filter(city='C')
        elif role == '9':  # 唐山总部财务
            shops = shops.filter(city='T')
        else:
            shops = shops.filter(shop_code=shop_code)

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
            sql = u" SELECT c.shop_code, c.`values` AS values_list, c.coupon_name, c.coupon_code, " \
                  u" c.start_date, c.end_date, c.`range` as range_list, jcs.used_amount, " \
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
                                                        end=endTime,
                                                        type=type,
                                                        shop=shop)

            conn = mth.getMysqlConn()
            cur = conn.cursor()
            cur.execute(sql)
            List = cur.fetchall()
            cur.close()
            conn.close()
        else:
            List = getDetail(code_list,start,end,shop)
            # serial = KfJobsCouponSn.objects.exclude(serial_id='0').filter(request_shop=shop,
            #                                                                  used_flag=1,
            #                                                                  used_date__lte=endTime,
            #                                                                  used_date__gte=start,
            #                                                                  used_shop__in=code_list)\
            #     .values('coupon_code').aggregate(serial_id=Max('serial_id'))
            # serial_id = []
            #for item_serial in serial:
                #serial_id.append(item_serial['serial_id'])

            # serial_id = str(serial_id)
            # serial_id = serial_id.replace('[', '').replace(']', '')
            # List = getDetail(code_list,start,endTime,shop,serial_id)

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
    sql = "select c.ShopID AS shop_code, count(c.CouponNO) AS common_amount, sum(ISNULL(ct.Value,0)) AS common_account " \
          "from MyShop_Coupon c,MyShop_CouponType ct " \
          " where c.ClearFlag = 1 and c.CouponTypeID like '8%' "\
          " and SUBSTRING(c.ClearSDate, 7,4)+'-'+LEFT(c.ClearSDate, 2)+'-'+replace(SUBSTRING(c.ClearSDate, 4,2),' ','0') "\
          "  BETWEEN '{start}' AND  '{end}' " \
          "   and c.CouponTypeID = ct.CouponTypeID and c.ClearShopID in ({shops})  "\
          " group by c.ShopID ".format(start=start,end=end,shops=shops)
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list

#def getDetail(used_shop, start, end, request_shop, serial_id):
def getDetail(used_shop, start, end, request_shop):
    """
    获取已使用券明细
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
    # u"   AND c.SerialID IN ({serial_id}) " \,serial_id=serial_id
    sql = u" SELECT c.ShopID AS shop_code, " \
          u"         ct.Value AS values_list, " \
          u"         ct.CouponTypeName AS coupon_name, " \
          u"         CONVERT(varchar(10), c.StartDate, 120) AS start_date, " \
          u"         c.EndDate AS end_date, " \
          u"         CASE WHEN ct.IfCurrShop = 0 THEN '全部店' " \
          u"          ELSE '发行店' END AS range_list, " \
          u"         count(c.CouponNO) AS used_amount, " \
          u"         ct.Value * count(c.CouponNO) AS used_account," \
          u"         c.SerialID AS serial_id," \
          u"         '0' AS coupon_code " \
          u" FROM MyShop_Coupon c, " \
          u"       MyShop_CouponType ct " \
          u" WHERE c.CouponTypeID = ct.CouponTypeID " \
          u"   AND c.ClearFlag = 1  and c.CouponTypeID like '8%' " \
          u"   AND c.ClearShopID IN ({code_list}) " \
          u"   AND SUBSTRING(c.ClearSDate, 7,4)+'-'+LEFT(c.ClearSDate, 2)+'-'+replace(SUBSTRING(c.ClearSDate, 4,2),' ','0') BETWEEN '{start}' AND '{end}' " \
          u"   AND c.ShopID = '{shop}' " \
          u" GROUP BY c.ShopID, " \
          u"           ct.Value, " \
          u"           ct.CouponTypeName, " \
          u"           CONVERT(varchar(10), c.StartDate, 120)," \
          u"           c.EndDate, " \
          u"           ct.IfCurrShop," \
          u"           c.SerialID ".format(code_list=used_shop,
                                            start=start,
                                            end=end,
                                            shop=request_shop)
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list