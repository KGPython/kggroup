# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import datetime, pymssql, json
from random import sample
from sellcard.common import Method as mth
from sellcard.models import KfJobsCoupon, KfJobsCouponGoodsDetail, KfJobsCouponBatch



@transaction.atomic
def index(request):
    """
    发行代金券列表controllers
    :param request:
    :return:列表view
    """
    shopid = request.session.get('s_shopcode')
    if shopid is None:
        shopid = '9999'
    today = str(datetime.date.today())
    couponType = mth.getReqVal(request, 'couponType', '')
    printed = mth.getReqVal(request, 'printed', '')
    issueSn = mth.getReqVal(request, 'issueSn', '')
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request, 'page', 1)

    kwargs = {}
    kwargs.setdefault('shopid', shopid)

    if couponType != '':
        kwargs.setdefault('coupontypeid', couponType)

    if printed != '':
        kwargs.setdefault('flag', printed)

    if issueSn != '':
        kwargs.setdefault('couponno__contains', issueSn)

    if start != '':
        kwargs.setdefault('startdate__gte', start)

    if end != '':
        kwargs.setdefault('startdate__lte', endTime)

    # 用于全部打印时传入的券号列表
    snlist = ','.join(KfJobsCoupon.objects.values_list('couponno', flat=True).filter(**kwargs))

    resList = KfJobsCoupon.objects.values(
        'shopid', 'createuserid', 'coupontypeid', 'batch', 'startdate', 'couponno', 'value',
        'giftvalue', 'rangeremark').filter(**kwargs).order_by('batch')

    paginator = Paginator(resList, 8)
    try:
        resList = paginator.page(page)
    except Exception as e:
        print(e)

    return render(request, 'voucher/issue/List.html', locals())


@transaction.atomic
def create(request):
    """
    新建代金券
    :param request:
    :return: 新建页view
    """
    goodList = []
    if request.method == 'POST':
        shop = request.session.get("s_shopcode")
        if (shop is None or shop == ''):
            shop = '9999'
        shopCode = request.session.get("s_shopcode")
        if (shopCode is None or shopCode == ''):
            shopCode = '9999'
        user = request.session.get("s_uid")
        amount = request.POST.get('amount')
        type = request.POST.get('type')
        if type == '3':
            chooseList = request.POST.get('chooseList')
            chooseList = json.loads(chooseList)
        else:
            chooseList = []
        costValue = request.POST.get('costValue')
        giftValue = request.POST.get('giftValue')
        if (giftValue is None or giftValue == ''):
            giftValue = 0
        discount = request.POST.get('discount')
        if (discount is None or discount == ''):
            discount = 0
        endDate = request.POST.get('endDate')
        CPwdFlag = request.POST.get('CPwdFlag')
        if CPwdFlag == '1':
            CPwd = request.POST.get('CPwd')
        else:
            CPwd = ''
        maxUseTime = request.POST.get('maxUseTime')
        if (maxUseTime is None or maxUseTime == ''):
            maxUseTime = 0
        rangeremark = request.POST.get('rangeremark')

        # 判断提交按钮类型：1、保存信息，2、查询商品
        if request.POST.get('buttonvalue') == '1':
            today = datetime.datetime.now().strftime('%Y%m%d')
            endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
            # 获取本次批次号：本次批号为历史最大批号加1，若不存在历史批号则为1
            batchs = KfJobsCouponBatch.objects.values('batch'
                                                      ).filter(shopid=shopCode,
                                                               createdate=today)
            batch = batchs.aggregate(Max('batch'))

            if batch['batch__max'] is None:
                batch = 1
            else:
                batch = int(batch['batch__max']) + 1
            batch = str(batch)
            # 拼接券号
            v_str = ''
            if shopCode[0:1] == 'C':
                v_str = '88814' + shopCode[2:] + today[2:]
            elif shopCode[0:1] == 'T':
                v_str = '88815' + shopCode[2:] + today[2:]
            else:
                v_str = '8889999' + datetime.datetime.now().strftime('%y%m%d')
            v_str = v_str + batch
            List = set()
            while len(List) < int(amount):
                sn = v_str + ''.join(sample('0123456789', 5))
                List.add(sn)

            # 插入卡券批次表
            KfJobsCouponBatch.objects.create(batch=batch,
                                             shopid=shopCode,
                                             createdate=today)
            # 插入卡券表
            for var_sn in List:
                KfJobsCoupon.objects.create(shopid=shop,
                                            batch=batch,
                                            couponno=var_sn,
                                            coupontypeid=type,
                                            startdate=datetime.datetime.now(),
                                            enddate=endDate,
                                            cpwdflag=CPwdFlag,
                                            cpwd=CPwd,
                                            usetime=0,
                                            maxusetime=maxUseTime,
                                            value=costValue,
                                            giftvalue=giftValue,
                                            discount=discount,
                                            flag=0,
                                            fromsheettype=220,
                                            rangeremark=rangeremark,
                                            createuserid=user,
                                            serialid=var_sn,
                                            clearflag=0,
                                            clearvalue=0)

            # 插入卡券商品明细表
            for var_good in chooseList:
                KfJobsCouponGoodsDetail.objects.create(batch=batch,
                                                       goodname=var_good['ShortName'].strip(),
                                                       goodcode=var_good['CustomNo'].strip(),
                                                       amount=int(var_good['amount']))

            # 传入代金券信息元组：
            #   shop：门店编码
            #   type：代金券类型
            #   （strat）：创建时间
            #   endDate：结束日期
            #   costValue：券面值
            #   batch：批次号
            #   v_str：执行存储过程参数
            tuple_info = (shop, type, datetime.datetime.now(), endDate, int(costValue), batch, v_str)

            # 插入SQL-sevser数据库调用方法
            InsertCoupon(tuple_info, List)
            msg = 1
        else:
            goodname = request.POST.get('goodname')
            goodcode = request.POST.get('goodcode')
            if (goodname == '' and goodcode == ''):
                goodList = []
            else:
                goodList = getGoodsList(goodname, goodcode)
    return render(request, 'voucher/issue/Create.html', locals())



def printed(request):
    """
    打印
    :param request:
    :return: 打印页view
    """
    snlist = mth.getReqVal(request, 'snlist', '')
    var_row = ''
    if snlist != '':
        snlist = snlist.split(',')
        A4 = int(mth.getReqVal(request, 'A4', '1'))

        if A4 == 9:
            tnop = 9  # The number of pages 每页显示个数
            A4_class = 'A4_transverse'
        else:
            tnop = 8  # The number of pages 每页显示个数
            A4_class = 'A4_longitudinal'

        counts = len(snlist)
        range_tnop = range(tnop)
        page_count = range(counts // tnop + (0 if counts % tnop == 0 else 1))

        resList = KfJobsCoupon.objects.values(
            'shopid', 'coupontypeid', 'enddate', 'couponno', 'rangeremark',
            'value', 'batch').filter(couponno__in=snlist)

        for var_i in resList:
            var_i['GoodList'] = KfJobsCouponGoodsDetail.objects.values(
                'goodname', 'goodcode', 'amount').filter(batch=var_i['batch'])

        print(resList)

    return render(request, 'voucher/issue/Print.html', locals())


def getGoodsList(goodsname, goodscode):
    """
    获取商品列表
    :param goodsname: 商品名称
    :param goodscode: 商品编码
    :return:列表
    """
    conn = pymssql.connect(host='192.168.122.141',
                           port='1433',
                           user='myshop',
                           password='oyf20140208HH',
                           database='mySHOPCMStock',
                           charset='utf8',
                           as_dict=True)
    cur = conn.cursor()
    sql = u"select ShortName, " \
          u"       CustomNo " \
          u"  from Goods " \
          u" where name like '%{goodsname}%'" \
          u"   and CustomNo like '%{goodscode}%'".format(goodsname=goodsname, goodscode=goodscode)
    cur.execute(sql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return list


def InsertCoupon(cardinfo, list):
    """
    插入久久表
    :param cardinfo: 代金券信息
    :param list: 代金券券号列表
    :return:信号值
    """
    conn = pymssql.connect(host='192.168.122.141',
                           port='1433',
                           user='myshop',
                           password='oyf20140208HH',
                           database='myshopcmcard',
                           charset='utf8',
                           as_dict=True)
    conn.autocommit(False)
    cur = conn.cursor()

    sql = u"Insert into MyShop_Coupon99" \
          u"(CouponID,ShopID,CouponNO,CouponTypeID,StartDate,EndDate," \
          u"CPWdFlag,CPwd,UseTime,MaxUseTime,Value," \
          u"Discount,Flag,FromSheetType,FromSDate,FromListNO," \
          u"FromPOSID,SerialID,ClearFlag)" \
          u"Values({coupon},{shop},{sn},{type},{start},{end}," \
          u"0,null,0,1,{value}," \
          u"0,0,220,null,null," \
          u"null,{batch},0)".format(coupon='%s',
                                    shop='%s',
                                    sn='%s',
                                    type='%s',
                                    start='%s',
                                    end='%s',
                                    value='%s',
                                    batch='%s')

    params = []

    for item in list:
        param = (cardinfo[6], cardinfo[0], item, cardinfo[1], cardinfo[2], cardinfo[3], cardinfo[4], cardinfo[6])
        params.append(param)

    try:
        cur.executemany(sql, params)
        conn.commit()

    except:
        conn.rollback()

    cur.close()
    cursor = conn.cursor()
    sql = "exec IF_MyShop_Coupon99 @CouponID='" + cardinfo[6] + "'"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return
