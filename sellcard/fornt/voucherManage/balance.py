# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.db import transaction
from django.shortcuts import render
import datetime, pymssql
from sellcard.common import Constants


@transaction.atomic
def index(request):
    """
    核销代金券controllers
    :param request:
    :return:视图view
    """
    if request.method == 'POST':
        voucherSn = request.POST.get('voucherSn')
        if request.POST.get('btn_value') == 'query':
            info = getInfo(voucherSn)
            if info is None:
                msg = 1
            elif info['ClearFlag'] != 0:
                msg = 2
            elif info['EndDate'] < datetime.datetime.now():
                msg = 3
            else:
                msg = 4
        if request.POST.get('btn_value') == 'save':
            shop = request.session.get("s_shopcode")
            if (shop is None or shop == ''):
                shop = '9999'
            UpdateCoupon(voucherSn, shop)
            msg = 5
    return render(request, 'voucher/balance/index.html', locals())


def getInfo(voucherSn):
    """
    获取商品列表
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
    sql = u"select ShopID," \
          u"        CouponNO," \
          u"        CouponTypeID," \
          u"        StartDate," \
          u"        EndDate," \
          u"        CPwdFlag," \
          u"        CPwd," \
          u"        ClearFlag," \
          u"        Value" \
          u"  from MyShop_Coupon " \
          u" where CouponNO = '{voucherSn}'".format(voucherSn=voucherSn)
    cur.execute(sql)
    v_info = cur.fetchone()
    cur.close()
    conn.close()
    return v_info


def UpdateCoupon(voucherSn, shop):
    """
    调存储过程核销
    :param voucherSn: 代金券信息
    :param shop: 代金券券号列表
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
    sql = "exec kgInsertCouponAcc99 @CouponNO='" + voucherSn + "', @ShopID='" + shop + "'"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return