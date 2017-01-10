# -*- coding:utf-8 -*-
__author__ = 'qixu'
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render
import datetime, pymssql, json
from sellcard.common import Constants
from sellcard.common import Method as mth
from sellcard.models import KfJobsCoupon, KfJobsCouponGoodsDetail, KfJobsCouponSn

@transaction.atomic
def index(request):
    """
    发行代金券列表controllers
    :param request:
    :return:列表view
    """
    shopcode = request.session.get('s_shopcode')
    if shopcode is None:
        shopcode = '9999'
    today = str(datetime.date.today())
    couponType = mth.getReqVal(request, 'couponType', '')
    printed = mth.getReqVal(request, 'printed', '')
    issueSn = mth.getReqVal(request, 'issueSn', '').strip()
    batch = mth.getReqVal(request, 'batch', '').strip()
    start = mth.getReqVal(request, 'start', today)
    end = mth.getReqVal(request, 'end', today)
    endTime = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    page = mth.getReqVal(request, 'page', 1)

    kwargs = {}
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
        'amount', 'print_amount', 'end_date', 'discount', 'range').filter(**kwargs).order_by('batch')

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
        sn_batch = mth.getReqVal(request, 'sn_batch', '')
        sn_start = mth.getReqVal(request, 'sn_start', '')
        sn_end = mth.getReqVal(request, 'sn_end', '')
        couponname = mth.getReqVal(request, 'couponname', '')
        pay_account = mth.getReqVal(request, 'pay_account', '')
        if (pay_account is None or pay_account == ''):
            pay_account = 0
        payment_type = mth.getReqVal(request, 'payment_type', '')
        type = mth.getReqVal(request, 'type', '')
        chooseList = mth.getReqVal(request, 'chooseList', '')
        chooseList = json.loads(chooseList)
        costValue = mth.getReqVal(request, 'costValue', '')
        if (costValue is None or costValue == ''):
            costValue = 0
        discount = mth.getReqVal(request, 'discount', '')
        if (discount is None or discount == ''):
            discount = 0
        endDate = mth.getReqVal(request, 'endDate', '')
        range = mth.getReqVal(request, 'range', '')
        rangeremark = ''
        if range == '0':
            rangeremark = '全部店'
        if range == '1':
            rangeremark = '发行店'

        # 判断提交按钮类型：1、保存信息，2、查询商品
        if mth.getReqVal(request, 'buttonvalue', '') == '1':
            today = datetime.datetime.now().strftime('%Y%m%d')
            if (endDate is not None and endDate != ''):
                endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
            else:
                endDate = datetime.datetime.strptime("9999-12-31", "%Y-%m-%d").date()
            name = request.session.get("s_unameChinese")

            # 获取本次批次号：本次批号为历史最大批号加1，若不存在历史批号则为1
            batchs = KfJobsCoupon.objects.values('batch'
                                                      ).filter(shop_code=shopCode,
                                                               create_date=today)
            batch = batchs.aggregate(Max('batch'))

            if batch['batch__max'] is None:
                batch = 1
            else:
                batch = int(batch['batch__max']) + 1
            batch = str(batch)
            v_str = ''
            if shopCode[0:1] == 'C':
                v_str = '88814' + shopCode[2:] + today[2:]
            elif shopCode[0:1] == 'T':
                v_str = '88815' + shopCode[2:] + today[2:]
            else:
                v_str = '8889999' + datetime.datetime.now().strftime('%y%m%d')
            coupon_code = shopCode+today[2:]+str(batch).zfill(2)
            serial_id = coupon_code

            sqlVoucher = u'select jcs.voucher ' \
                         u'  from kf_jobs_coupon_sn jcs ' \
                         u' where jcs.batch = "{batch}" ' \
                         u'   and jcs.request_shop = "{shop}" ' \
                         u'   and jcs.state = 1 ' \
                         u'   and jcs.sn between "{sn_start}" and "{sn_end}"'.format(batch=sn_batch,
                                                                                     shop=shopCode,
                                                                                     sn_start=sn_start.zfill(6),
                                                                                     sn_end=sn_end.zfill(6))
            conn = mth.getMysqlConn()
            cur = conn.cursor()
            cur.execute(sqlVoucher)
            List = cur.fetchall()
            cur.close()
            conn.close()

            len_list = len(List)

            if len_list != 0:
                # 插入卡券批次表
                KfJobsCoupon.objects.create(coupon_code=coupon_code,
                                            coupon_name=couponname,
                                            batch=batch,
                                            shop_code=shop,
                                            type=type,
                                            values=costValue,
                                            start_date=datetime.datetime.now(),
                                            end_date=endDate,
                                            range=rangeremark,
                                            payment_type=payment_type,
                                            pay_account=pay_account,
                                            credit_account=0,
                                            discount=discount,
                                            amount=len_list,
                                            print_amount=0,
                                            state=0,
                                            remark='',
                                            create_uesr_id=user,
                                            create_user_name=name,
                                            create_date=today,
                                            start_sn=sn_start.zfill(6),
                                            end_sn=sn_end.zfill(6))

                # 插入卡券商品明细表
                for var_good in chooseList:
                    KfJobsCouponGoodsDetail.objects.create(batch=coupon_code,
                                                           goodname=var_good['ShortName'].strip(),
                                                           goodcode=var_good['CustomNo'].strip(),
                                                           amount=var_good['amount'])

                if type == '3':
                    # 传入代金券信息元组：
                    # 0：shop：门店编码
                    #   1：couponname：代金券类型名称
                    #   2：（strat）：创建时间
                    #   3：endDate：结束日期
                    #   4：costValue：券面值
                    #   5：serial_id：批次号
                    #   6：coupon_code：执行存储过程参数
                    #   7：name：操作人姓名
                    #   8：range：是否限定使用范围：0）不限定，1）本店
                    tuple_info = (
                        shop, couponname, datetime.datetime.now(), endDate, int(costValue), serial_id, coupon_code, name, range)
                    # 插入SQL-sevser数据库调用方法
                    InsertCoupon(tuple_info, List)
                else:
                    serial_id = '0'

                #修改验证码表
                for var_vou in List:
                    KfJobsCouponSn.objects.filter(batch=sn_batch,
                                                  request_shop=shopCode,
                                                  state=1,
                                                  voucher=var_vou['voucher']).update(state=2,
                                                                                     coupon_code=coupon_code,
                                                                                     serial_id=serial_id)
                msg = 1
            else:
                msg = 2
        else:
            goodname = mth.getReqVal(request, 'goodname', '')
            goodcode = mth.getReqVal(request, 'goodcode', '')
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
    coupon_code = mth.getReqVal(request, 'coupon_code', '')
    is_show = mth.getReqVal(request, 'is_show', '')
    counts = int(mth.getReqVal(request, 'counts', ''))

    resList = KfJobsCoupon.objects.values(
            'shop_code', 'coupon_name', 'type', 'start_date', 'end_date', 'range', 'print_amount',
            'values', 'batch', 'coupon_code', 'start_sn', 'end_sn').filter(coupon_code=coupon_code)
    resList = resList[0]
    print_amount = resList['print_amount'] + counts
    KfJobsCoupon.objects.filter(coupon_code=coupon_code).update(print_amount=print_amount)

    GoodList = KfJobsCouponGoodsDetail.objects.values(
        'goodname', 'goodcode', 'amount').filter(batch=coupon_code)

    good_len = len(GoodList)
    tnop = 1 # The number of pages 每页显示个数
    if good_len <= 4:
        tnop = 10
    elif good_len>4 and good_len<=8:
        tnop = 8
    else:
        tnop = 6
    range_tnop = range(tnop)
    page_count = range(counts // tnop + (0 if counts % tnop == 0 else 1))

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
            #   1：couponname：代金券类型名称
            #   2：（strat）：创建时间
            #   3：endDate：结束日期
            #   4：costValue：券面值
            #   5：serial_id：批次号
            #   6：coupon_code：执行存储过程参数
            #   7：name：操作人姓名
            #   8：range：是否限定使用范围：0）不限定，1）本店
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
                                                   ifcurrshop=cardinfo[8])
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
          u"Values({coupon},{shop},{sn},{type},GETdate(),{end}," \
          u"0,null ,0,1,{value}," \
          u"0,0,220,{create},null," \
          u"{name},{batch},0)".format(coupon='%s',
                                      shop='%s',
                                      sn='%s',
                                      type='%s',
                                      end='%s',
                                      value='%s',
                                      create='%s',
                                      name='%s',
                                      batch='%s')

    params = []

    for item in list:
        param = (
            cardinfo[6],
            cardinfo[0],
            item['voucher'],
            type,
            cardinfo[3],
            cardinfo[4],
            cardinfo[2],
            cardinfo[7],
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
