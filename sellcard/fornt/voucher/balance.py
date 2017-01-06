# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.db import transaction
from django.shortcuts import render
import datetime, pymssql
from sellcard.common import Constants
from sellcard.common import Method as mth
from sellcard.models import KfJobsCoupon, KfJobsCouponSn

@transaction.atomic
def index(request):
    """
    核销代金券controllers
    :param request:
    :return:视图view
    """
    if request.method == 'POST':
        voucherSn = mth.getReqVal(request, 'voucherSn', '').strip()
        if mth.getReqVal(request, 'btn_value', '') == 'query':
            data_info = KfJobsCouponSn.objects.values('state','coupon_code','serial_id','used_flag'
                                                   ).filter(voucher=voucherSn)
            if data_info is None:
                msg = 1
            elif data_info[0]['state'] != 2:
                msg = 1
            elif data_info[0]['used_flag'] == 1:
                msg = 2
            elif data_info[0]['serial_id'] != '0':
                info = getInfo(voucherSn)
                if info is None:
                    msg = 1
                elif info['ClearFlag'] != 0:
                    msg = 2
                elif info['end_date'] < datetime.datetime.now():
                    msg = 3
                else:
                    msg = 4
            else:
                info = KfJobsCoupon.objects.values('shop_code','type','start_date','end_date','values'
                                                   ).filter(coupon_code=data_info[0]['coupon_code'])
                if info is None:
                    msg = 1
                elif info[0]['end_date'] < datetime.datetime.now():
                    msg = 3
                else:
                    info = info[0]
                    info['spend'] = info['values']
                    msg = 4
        if  mth.getReqVal(request, 'btn_value', '') == 'save':
            spend = mth.getReqVal(request, 'spend', '')
            type = mth.getReqVal(request, 'type', '')
            shop = request.session.get("s_shopcode")
            name = request.session.get("s_unameChinese")
            if (shop is None or shop == ''):
                shop = '9999'
            if type == '通用券':
                UpdateCoupon(voucherSn, shop, spend, name)# 调用ERP过程

            # 修改验证码表
            KfJobsCouponSn.objects.filter(voucher=voucherSn).update(used_flag=1,
                                                                    used_shop=shop,
                                                                    used_name=name,
                                                                    used_date=datetime.datetime.now())
            msg = 5
        if  mth.getReqVal(request, 'btn_value', '') == 'old':
            info = getInfo(voucherSn)
            if info is None:
                msg = 1
            elif info['ClearFlag'] != 0:
                msg = 2
            elif info['end_date'] < datetime.datetime.now():
                msg = 3
            else:
                msg = 4
    return render(request, 'voucher/balance/index.html', locals())


def getInfo(voucherSn):
    """
    获取券信息
    :param voucherSn: 核销券号
    :return:券信息
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    cur = conn.cursor()
    sql = u"select ShopID as shop_code," \
          u"        CouponNO," \
          u"        CouponTypeID," \
          u"        3 as type," \
          u"        StartDate as start_date," \
          u"        EndDate as end_date," \
          u"        ClearFlag," \
          u"        Value as spend" \
          u"  from MyShop_Coupon " \
          u" where CouponNO = '{voucherSn}'".format(voucherSn=voucherSn)
    cur.execute(sql)
    v_info = cur.fetchone()
    cur.close()
    conn.close()
    return v_info


def UpdateCoupon(voucherSn, shop, spend, name):
    """
    调存储过程核销
    :param voucherSn: 代金券号
    :param shop: 核销门店
    :param spend: 花费
    :param name: 操作人姓名
    :return:void
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    conn.autocommit(False)
    cursor = conn.cursor()
    sql = "exec kgInsertCouponAcc99 @CouponNO='" + voucherSn + "', @ShopID='" + shop + "', @sValue=" + spend + ", @clearnote ='" + name + "'"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return