# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
import datetime, pymssql, json
from random import sample
from sellcard.common import Constants
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
    batch = mth.getReqVal(request, 'batch', '')
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

    if batch != '':
        kwargs.setdefault('batch', batch)

    if issueSn != '':
        kwargs.setdefault('couponno__contains', issueSn)

    if start != '':
        kwargs.setdefault('startdate__gte', start)

    if end != '':
        kwargs.setdefault('startdate__lte', endTime)

    # 用于全部打印时传入的券号列表
    snlist = ','.join(KfJobsCoupon.objects.values_list('couponno', flat=True).filter(**kwargs))

    List = KfJobsCoupon.objects.values(
        'shopid', 'createuserid', 'coupontypeid', 'batch', 'startdate', 'couponno', 'value',
        'giftvalue', 'rangeremark').filter(**kwargs).order_by('batch')

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
        name = request.POST.get('name')

        type = request.POST.get('type')
        chooseList = request.POST.get('chooseList')
        chooseList = json.loads(chooseList)

        costValue = request.POST.get('costValue')
        if (costValue is None or costValue == ''):
            costValue = 0
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
        range = request.POST.get('range')
        rangeremark = ''
        if range == '0':
            rangeremark = '全部店'
        if range == '1':
            rangeremark = '发行店'

        # 判断提交按钮类型：1、保存信息，2、查询商品
        if request.POST.get('buttonvalue') == '1':
            today = datetime.datetime.now().strftime('%Y%m%d')
            if (endDate is not None and endDate != ''):
                endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
            else:
                endDate = datetime.datetime.strptime("9999-12-31", "%Y-%m-%d").date()
            name = request.session.get("s_uname")

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
            batch_sn = v_str[3:]
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
                                            couponname=name,
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
                KfJobsCouponGoodsDetail.objects.create(batch=batch_sn,
                                                       goodname=var_good['ShortName'].strip(),
                                                       goodcode=var_good['CustomNo'].strip(),
                                                       amount=int(var_good['amount']))


            # 传入代金券信息元组：
            # 0：shop：门店编码
            #   1：name：代金券类型名称
            #   2：（strat）：创建时间
            #   3：endDate：结束日期
            #   4：costValue：券面值
            #   5：batch：批次号
            #   6：v_str：执行存储过程参数
            #   7：CPwdFlag：是否需要密码
            #   8：CPwd：密码
            #   9：name：操作人姓名
            #   10：range：是否限定使用范围：0）不限定，1）本店
            tuple_info = (
                shop, name, datetime.datetime.now(), endDate, int(costValue), batch, v_str, CPwdFlag, CPwd, name,
                range)

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
            'shopid', 'couponname', 'coupontypeid','startdate', 'enddate', 'couponno', 'rangeremark',
            'value', 'batch').filter(couponno__in=snlist)

        for var_i in resList:
            var_i['value'] ='{:.2f}'.format(var_i['value'])
            batch =''
            if var_i['shopid'][0:1] == 'C':
                batch = '14' + var_i['shopid'][2:]+ var_i['startdate'].strftime('%y%m%d')+ var_i['batch']
            elif var_i['shopid'][0:1] == 'T':
                batch = '15' + var_i['shopid'][2:]+ var_i['startdate'].strftime('%y%m%d')+ var_i['batch']
            var_i['GoodList'] = KfJobsCouponGoodsDetail.objects.values(
                'goodname', 'goodcode', 'amount').filter(batch=batch)

    return render(request, 'voucher/issue/Print.html', locals())


def getGoodsList(goodsname, goodscode):
    """
    获取商品列表
    :param goodsname: 商品名称
    :param goodscode: 商品编码
    :return:列表
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_STOCK_SERVER,
                           port=Constants.KGGROUP_DB_STOCK_PORT,
                           user=Constants.KGGROUP_DB_STOCK_USER,
                           password=Constants.KGGROUP_DB_STOCK_PASSWORD,
                           database=Constants.KGGROUP_DB_STOCK_DATABASE,
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
    插入第三方库
    :param cardinfo: 代金券信息
            #   0：shop：门店编码
            #   1：name：代金券类型名称
            #   2：（strat）：创建时间
            #   3：endDate：结束日期
            #   4：costValue：券面值
            #   5：batch：批次号
            #   6：v_str：执行存储过程参数
            #   7：CPwdFlag：是否需要密码
            #   8：CPwd：密码
            #   9：name：操作人姓名
            #   10：range：是否限定使用范围：0）不限定，1）本店
    :param list: 代金券券号列表
    :return:信号值
    """
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=True)
    conn.autocommit(False)
    # 插入类型表
    typecursor = conn.cursor()
    sql = u" SELECT " \
          u" CASE " \
          u" WHEN MAX (CouponTypeID) IS NULL THEN " \
          u"   800000001 " \
          u" ELSE " \
          u"   MAX (CouponTypeID) + 1 " \
          u" END AS CouponTypeID " \
          u" FROM " \
          u"	MyShop_CouponType " \
          u" WHERE " \
          u"	CouponTypeID LIKE '8%' "
    typecursor.execute(sql)
    type = typecursor.fetchone()
    type = type['CouponTypeID']

    sql = u"insert into MyShop_CouponType" \
          u"(ShopID,CouponTypeID,CouponTypeName,CouponFlag,ValidDay," \
          u" StartDate,EndDate,Value,MaxValue,Discount," \
          u" Note,PayValue,UseScope,IfCurrShop,EnableValue,PayType)" \
          u"values(" \
          u" 'K001',{coupontypeid},'{coupontypename}',2,0," \
          u" GETdate(),{EndDate},{value},null,100," \
          u" '',0.00,1,{ifcurrshop},0,'') ".format(coupontypeid=type,
                                                   coupontypename=cardinfo[1],
                                                   EndDate=cardinfo[3],
                                                   value=cardinfo[4],
                                                   ifcurrshop=cardinfo[10])
    typecursor.execute(sql)
    conn.commit()
    typecursor.close()

    cur = conn.cursor()
    # 插入临时久久表
    sql = u"Insert into MyShop_Coupon99" \
          u"(CouponID,ShopID,CouponNO,CouponTypeID,StartDate,EndDate," \
          u"CPWdFlag,CPwd,UseTime,MaxUseTime,Value," \
          u"Discount,Flag,FromSheetType,FromSDate,FromListNO," \
          u"FromPOSID,SerialID,ClearFlag)" \
          u"Values({coupon},{shop},{sn},{type},{start},{end}," \
          u"{CPWdFlag},{CPwd},0,1,{value}," \
          u"0,0,220,{create},null," \
          u"{name},{batch},0)".format(coupon='%s',
                                      shop='%s',
                                      sn='%s',
                                      type='%s',
                                      start='%s',
                                      end='%s',
                                      CPWdFlag='%s',
                                      CPwd='%s',
                                      value='%s',
                                      create='%s',
                                      name='%s',
                                      batch='%s')

    params = []

    for item in list:
        param = (
            cardinfo[6],
            cardinfo[0],
            item,
            type,
            cardinfo[2],
            cardinfo[3],
            cardinfo[7],
            cardinfo[8],
            cardinfo[4],
            cardinfo[2],
            cardinfo[9],
            cardinfo[6])
        params.append(param)

    try:
        cur.executemany(sql, params)
        conn.commit()

    except:
        conn.rollback()

    cur.close()
    cursor = conn.cursor()
    # 读取久久表调用存储过程插入正式表
    sql = "exec IF_MyShop_Coupon99 @CouponID='" + cardinfo[6] + "'"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return
