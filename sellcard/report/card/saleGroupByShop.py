#-*- coding:utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import OrderUpCard,Payment
from sellcard.common import Method as mth
from sellcard import views as base


def index(request):
    shop = request.session.get('s_shopcode','')
    role_id = request.session.get('s_roleid')
    if request.method == 'GET':
        start = str(datetime.date.today().replace(day=1))
        end = str(datetime.date.today())
        endTime =str(datetime.date.today()+datetime.timedelta(1))
    if request.method == 'POST':
        today = datetime.date.today()
        start = request.POST.get('start',today)
        end = request.POST.get('end',today)
        endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))

    conn = mth.getMysqlConn()
    cur = conn.cursor()
    if role_id == '1' or role_id == '6':
        shops = mth.getCityShops()
        shopsCode = mth.getCityShopsCode()
    if role_id == '9':
        shops = mth.getCityShops('T')
        shopsCode = mth.getCityShopsCode('T')
    if role_id == '8':
        shops = mth.getCityShops('C')
        shopsCode = mth.getCityShopsCode('C')
    if role_id == '10' or role_id == '2':
        shops = base.findShop(shop)
        shopsCode = [shop]

    shopsCodeStr = "'" + "','".join(shopsCode) + "'"
    # shopsCodeStr = "('C003')"

    # saleDiscGroupByShop = 'SELECT a.shop_code, SUM(CASE WHEN b.card_balance<= a.diff_price THEN a.y_cash+b.card_balance ELSE a.disc_amount END ) AS disc,' \
    #                       'SUM(a.y_cash) AS disc_cash,SUM(case WHEN b.card_balance<= a.diff_price THEN b.card_balance ELSE b.card_balance-a.diff_price END) AS disc_card ' \
    #                       'FROM orders AS a ' \
    #                       'LEFT JOIN (SELECT  order_id,SUM(card_balance) AS card_balance ' \
    #                       'FROM order_info WHERE card_attr="2" GROUP BY order_id,card_attr) AS b ' \
    #                       'ON b.order_id = a.order_sn ' \
    #                       'WHERE a.add_time >= "{start}" AND a.add_time <= "{end}" AND a.shop_code IN ({shopsCodeStr}) group by a.shop_code '\
    #                      .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)

    saleDiscGroupByShop = 'select shop_code,'\
                          'SUM(case when disc_amount>=y_cash then disc_amount else diff_price+disc_amount end) as disc, '\
                          'SUM(y_cash) as disc_cash, '\
                          'SUM(case when disc_amount>=y_cash then disc_amount-y_cash else disc_amount+diff_price-y_cash end) as disc_card ' \
                          'from orders ' \
                          'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr})' \
                          'group by shop_code ' \
                        .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(saleDiscGroupByShop)
    saleDiscList = cur.fetchall()

    salePayGroupByShop = 'select ord.shop_code,info.pay_id,info.change_time,info.is_pay,SUM(info.pay_value) as pay_value ' \
                'from orders as ord , order_payment_info as info ' \
                'where ord.add_time>="{start}" and ord.add_time<="{end}" and ord.shop_code in ({shopsCodeStr}) and ord.order_sn = info.order_id ' \
                'group by ord.shop_code,info.pay_id,info.change_time ' \
                .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(salePayGroupByShop)
    salePayList = cur.fetchall()

    fillList = OrderUpCard.objects\
            .values('shop_code')\
            .filter(add_time__gte=start,add_time__lte=endTime,shop_code__in=shopsCode)\
            .annotate(fill=Sum('diff_price'))\
            .order_by('shop_code')

    # changeDiscGroupByShop = 'SELECT a.shop_code, SUM(CASE WHEN b.card_balance<= a.disc_pay THEN a.disc_cash+b.card_balance ELSE a.disc END) AS disc,' \
    #                         'SUM(a.disc_cash) AS disc_cash,SUM(case WHEN b.card_balance<= a.disc_pay THEN b.card_balance ELSE b.card_balance-a.disc_pay END) AS disc_card ' \
    #                         'FROM order_change_card AS a '\
    #                         'LEFT JOIN (SELECT  order_sn,sum(card_balance) as card_balance ' \
    #                         'FROM order_change_card_info where type="1" group by order_sn,type)'\
    #                         'AS b on b.order_sn = a.order_sn '\
    #                         'WHERE a.add_time >= "{start}" AND a.add_time <= "{end}" AND a.shop_code IN ({shopsCodeStr}) ' \
    #                         'group by a.shop_code ' \
    #                         .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)

    changeDiscGroupByShop = 'select shop_code,SUM(case when disc>=disc_cash then disc else disc_pay+disc end) as disc,' \
                            'SUM(disc_cash) as disc_cash,' \
                            'SUM(case when disc>=disc_cash then disc-disc_cash else disc+disc_pay-disc_cash end) as disc_card ' \
                            'from order_change_card ' \
                            'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr}) ' \
                            'group by shop_code ' \
        .format(start=start, end=endTime, shopsCodeStr=shopsCodeStr)
    cur.execute(changeDiscGroupByShop)
    changeDiscList = cur.fetchall()
    changePayGroupByShop = 'select ord.shop_code ,info.pay_id,info.change_time,SUM(info.pay_value) as pay_value ' \
                           'from order_change_card as ord , order_change_card_payment as info ' \
                           'where ord.add_time>="{start}" and ord.add_time<="{end}" and shop_code in ({shopsCodeStr}) and ord.order_sn = info.order_id ' \
                           'group by ord.shop_code,info.pay_id,info.change_time' \
                           .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(changePayGroupByShop)
    changePayList = cur.fetchall()

    paymentsRate = Payment.objects.values('id', 'dis_rate').filter(dis_rate__gte=0)
    paymentsRateDict = {item['id']: float(item['dis_rate']) for item in paymentsRate}
    totalDict  = {'discTotal':0,
                  'discCashTotal':0,'total_disc_6':0,'total_disc_7':0,'total_disc_8':0,'total_disc_10':0,'total_disc_11':0,'total_disc_qita':0,'discCardTotal':0,
                  'inSubTotal':0,'total_1':0,'total_2':0,'total_3':0,
                  'total_4_0':0,'total_4_1':0,'total_5':0,'total_6':0,'total_7':0,'total_8':0,'total_9':0,'total_10':0,'total_11':0,}

    dataList = []
    for i in range(0,len(shops)):
        shopcode = shops[i]['shop_code']
        if shops[i]['shop_code'] != 'ZBTG':
            item = {'shop_code':'',
                    'disc':0,'disc_6':0,'disc_7':0,'disc_8':0,'disc_10':0,'disc_11':0,'disc_cash':0,'disc_card':0,
                    'inSub':0,'pay_1':0,'pay_2':0,'pay_3':0,'pay_4_1':0,'pay_4_0':0,'pay_5':0,'pay_6':0,'pay_7':0,'pay_8':0,
                    'pay_9':0,'pay_10':0,'pay_11':0,}
            item['shop_code'] = shops[i]['shop_code']
            for sale in salePayList:
                if sale['shop_code']==item['shop_code']:
                    #横向各门店售卡汇总赋值
                    pay_id = sale['pay_id']
                    if sale['pay_id'] == 1:
                        item['pay_1'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 2:
                        item['pay_2'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 3:
                        item['pay_3'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 4 and sale['is_pay'] == '0':
                        item['pay_4_0'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['change_time']:
                        item['pay_4_1'] += float(sale['pay_value'])
                    if sale['pay_id'] == 5:
                        item['pay_5'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 6:
                        item['pay_6'] += float(sale['pay_value'])
                        item['disc_6'] += float(sale['pay_value'])*paymentsRateDict[6]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 7:
                        item['pay_7'] += float(sale['pay_value'])
                        item['disc_7'] += float(sale['pay_value']) * paymentsRateDict[7]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 8:
                        item['pay_8'] += float(sale['pay_value'])
                        item['disc_8'] += float(sale['pay_value']) * paymentsRateDict[8]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 9:
                        item['pay_9'] += float(sale['pay_value'])
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 10:
                        item['pay_10'] += float(sale['pay_value'])
                        item['disc_10'] += float(sale['pay_value']) * paymentsRateDict[10]
                        item['inSub'] += float(sale['pay_value'])
                    if sale['pay_id'] == 11:
                        item['pay_11'] += float(sale['pay_value'])
                        item['disc_11'] += float(sale['pay_value']) * paymentsRateDict[11]
                        item['inSub'] += float(sale['pay_value'])



            for saleDisc in saleDiscList:
                if saleDisc['shop_code'] == item['shop_code']:
                    if not saleDisc['disc']:
                        saleDisc['disc'] = 0
                    if not saleDisc['disc_cash']:
                        saleDisc['disc_cash'] = 0
                    if not saleDisc['disc_card']:
                        saleDisc['disc_card'] = 0
                    elif saleDisc['disc_card']>0:
                        item['disc_card'] += float(saleDisc['disc_card'])
                    item['disc'] += float(saleDisc['disc'])
                    item['disc_cash'] += float(saleDisc['disc_cash'])


            for fill in fillList:
                if item['shop_code'] == fill['shop_code']:
                    if not fill['fill']:
                        fill['fill']=0

                    item['pay_1'] += float(fill['fill'])
                    item['inSub'] += float(fill['fill'])

            for change in changePayList:
                if item['shop_code'] == change['shop_code']:
                    # 横向各门店售卡汇总赋值
                    if change['pay_id'] == 1:
                        item['pay_1'] += float(change['pay_value'])
                    if change['pay_id'] == 2:
                        item['pay_2'] += float(change['pay_value'])
                    if change['pay_id'] == 3:
                        item['pay_3'] += float(change['pay_value'])
                    if change['pay_id'] == 5:
                        item['pay_5'] += float(change['pay_value'])
                    if change['pay_id'] == 6:
                        item['pay_6'] += float(change['pay_value'])
                        item['disc_6'] += float(change['pay_value']) * paymentsRateDict[6]
                    if change['pay_id'] == 7:
                        item['pay_7'] += float(change['pay_value'])
                        item['disc_7'] += float(change['pay_value']) * paymentsRateDict[7]
                    if change['pay_id'] == 8:
                        item['pay_8'] += float(change['pay_value'])
                        item['disc_8'] += float(change['pay_value']) * paymentsRateDict[8]
                    if change['pay_id'] == 9:
                        item['pay_9'] += float(change['pay_value'])
                    if change['pay_id'] == 10:
                        item['pay_10'] += float(change['pay_value'])
                        item['disc_10'] += float(change['pay_value']) * paymentsRateDict[10]
                    if change['pay_id'] == 11:
                        item['pay_11'] += float(change['pay_value'])
                        item['disc_11'] += float(change['pay_value']) * paymentsRateDict[11]

                    item['inSub'] += float(change['pay_value'])

            for changeDisc in changeDiscList:
                if changeDisc['shop_code'] == item['shop_code']:
                    if not changeDisc['disc']:
                        changeDisc['disc'] = 0
                    if not changeDisc['disc_cash']:
                        changeDisc['disc_cash'] = 0
                    if not changeDisc['disc_card']:
                        changeDisc['disc_card'] = 0

                    item['disc'] += float(changeDisc['disc'])
                    item['disc_cash'] += float(changeDisc['disc_cash'])
                    item['disc_card'] += float(changeDisc['disc_card'])

            totalDict['discTotal'] += item['disc']
            totalDict['discCashTotal'] += item['disc_cash']
            totalDict['total_disc_6'] += item['disc_6']
            totalDict['total_disc_7'] += item['disc_7']
            totalDict['total_disc_8'] += item['disc_8']
            totalDict['total_disc_10'] += item['disc_10']
            totalDict['total_disc_11'] += item['disc_11']
            totalDict['discCardTotal'] += item['disc_card']
            totalDict['inSubTotal'] += item['inSub']
            totalDict['total_1'] += item['pay_1']
            totalDict['total_2'] += item['pay_2']
            totalDict['total_3'] += item['pay_3']
            totalDict['total_4_0'] += item['pay_4_0']
            totalDict['total_4_1'] += item['pay_4_1']
            totalDict['total_5'] += item['pay_5']
            totalDict['total_6'] += item['pay_6']
            totalDict['total_7'] += item['pay_7']
            totalDict['total_8'] += item['pay_8']
            totalDict['total_9'] += item['pay_9']
            totalDict['total_10'] += item['pay_10']
            totalDict['total_11'] += item['pay_11']

            dataList.append(item)
    totalDict['total_disc_qita'] = totalDict['discCashTotal']-totalDict['total_disc_6']-totalDict['total_disc_7']\
                                   -totalDict['total_disc_8']-totalDict['total_disc_10']-totalDict['total_disc_11']

    return render(request, 'report/card/saleGroupByShop/index.html', locals())




def detail(request):
    today = datetime.date.today()
    page = mth.getReqVal(request, 'page', 1)
    shop_code = request.GET.get('shop')
    pay_id = request.GET.get('pay_id')

    shop = request.session.get('s_shopcode', '')
    role_id = request.session.get('s_roleid')
    if role_id == '9':
        shopsCode = mth.getCityShopsCode('T')
        if shop_code not in shopsCode:
            return render(request, '500.html', locals())
    if role_id == '8':
        shopsCode = mth.getCityShopsCode('C')
        if shop_code not in shopsCode:
            return render(request, '500.html', locals())
    if role_id == '10' or role_id == '2':
        if shop != shop_code:
            return render(request, '500.html', locals())



    if pay_id == '2':
        pay_name = '代金券'
    if pay_id == '3':
        pay_name = '汇款'
    if pay_id == '4':
        pay_name = '赊账'
    if pay_id == '5':
        pay_name = 'Pos'
    if pay_id == '6':
        pay_name = '移动积分'
    if pay_id == '7':
        pay_name = '美团'
    if pay_id == '8':
        pay_name = '糯米'
    if pay_id == '9':
        pay_name = '黄金手'
    if pay_id == '10':
        pay_name = '慧购线上'
    if pay_id == '11':
        pay_name = '慧购线下'

    start = request.GET.get('start', today)
    end = request.GET.get('end', today)
    endTime = str(datetime.datetime.strptime(end, '%Y-%m-%d').date() + datetime.timedelta(1))

    conn = mth.getMysqlConn()
    cur = conn.cursor()

    sqlstr = u"select ord.order_sn," \
             u"        case" \
             u"        when ord.action_type = '1' then" \
             u"           '单卡售卡'" \
             u"        when ord.action_type = '2' then" \
             u"           '批量售卡'" \
             u"        when ord.action_type = '3' then" \
             u"           '借卡结算'" \
             u"        when ord.action_type = '5' then" \
             u"	          '实物团购返点'" \
             u"        else" \
             u"	          '其它售卡'" \
             u"        end as action_type," \
             u"       ord.buyer_name as user_name," \
             u"       ord.buyer_tel as user_phone," \
             u"       ord.buyer_company as user_company," \
             u"       opi.bank_name," \
             u"       opi.bank_sn," \
             u"       opi.pay_company," \
             u"       opi.pay_value," \
             u"        case" \
             u"        when opi.is_pay = '1' then" \
             u"           '已到账'" \
             u"        when opi.is_pay = '0' then" \
             u"           '未到账'" \
             u"        end as is_pay" \
             u"  from orders ord, order_payment_info opi" \
             u" where ord.shop_code = '{shop_code_ord}' " \
             u"   and ord.add_time >= '{start_ord}' " \
             u"   and ord.add_time <= '{end_ord}'" \
             u"   and ord.order_sn = opi.order_id" \
             u"   and opi.pay_id = {pay_id_ord}" \
             u" union " \
             u"select occ.order_sn, " \
             u"        case" \
             u"        when occ.action_type = '1' then" \
             u"           '大面值换小面值'" \
             u"        when occ.action_type = '2' then" \
             u"	          '小面值换大面值'" \
             u"        else" \
             u"	          '其它换卡'" \
             u"        end as action_type," \
             u"       occ.user_name," \
             u"       occ.user_phone," \
             u"       '' as user_company," \
             u"       occp.bank_name," \
             u"       occp.bank_sn," \
             u"       occp.pay_company," \
             u"       occp.pay_value," \
             u"        case" \
             u"        when occp.is_pay = '1' then" \
             u"           '已到账'" \
             u"        when occp.is_pay = '0' then" \
             u"           '未到账'" \
             u"        end as is_pay" \
             u"  from order_change_card occ, order_change_card_payment occp" \
             u" where occ.shop_code = '{shop_code_occ}' " \
             u"   and occ.add_time >= '{start_occ}' " \
             u"   and occ.add_time <= '{end_occ}'" \
             u"   and occ.order_sn = occp.order_id" \
             u"   and occp.pay_id = {pay_id_occ}" \
        .format(shop_code_ord=shop_code,
                start_ord=start,
                end_ord=endTime,
                pay_id_ord=pay_id,
                shop_code_occ=shop_code,
                start_occ=start,
                end_occ=endTime,
                pay_id_occ=pay_id)
    cur.execute(sqlstr)
    List = cur.fetchall()

    for item in List:
        item['pay_value'] = float(item['pay_value'])
    # paginator = Paginator(List, 20)
    #
    # try:
    #     List = paginator.page(page)
    #
    #     if List.number > 1:
    #         page_up = List.previous_page_number
    #     else:
    #         page_up = 1
    #
    #     if List.number < List.paginator.num_pages:
    #         page_down = List.next_page_number
    #     else:
    #         page_down = List.paginator.num_pages

    # except Exception as e:
    #     print(e)
    return render(request, 'report/card/saleGroupByShop/Detail.html', locals())

def date_detail(request):
    shopcode = mth.getReqVal(request, 'shopcode','')
    start = mth.getReqVal(request, 'start','')
    end = mth.getReqVal(request, 'end','')
    endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))
    page = mth.getReqVal(request, 'page', 1)

    conn = mth.getMysqlConn()
    cur = conn.cursor()

    sql = u" select d.date_time, sum(d.disc) as disc, sum(d.disc_cash) as disc_cash, sum(d.disc_card) as disc_card, " \
          u" sum(d.pay_1) as pay_1, sum(d.pay_2) as pay_2, sum(d.pay_3) as pay_3, sum(d.pay_4) as pay_4, " \
          u" sum(d.pay_5) as pay_5, sum(d.pay_6) as pay_6, sum(d.pay_7) as pay_7, sum(d.pay_8) as pay_8, " \
          u" sum(d.pay_9) as pay_9, sum(d.pay_10) as pay_10, sum(d.pay_11) as pay_11, sum(d.disc_6) as disc_6, " \
          u" sum(d.disc_7) as disc_7, sum(d.disc_8) as disc_8, sum(d.disc_10) as disc_10, sum(d.disc_11) as disc_11,  " \
          u" sum(d.inSub) as inSub FROM (select DATE_FORMAT( o.add_time, '%Y-%m-%d') as date_time, " \
          u" o.disc_amount as disc, o.y_cash as disc_cash, o.disc_amount - o.y_cash as disc_card, " \
          u" a.pay_1, a.pay_2, a.pay_3, a.pay_4, a.pay_5, a.pay_6, a.pay_7, a.pay_8, a.pay_9, a.pay_10, a.pay_11, " \
          u" a.disc_6, a.disc_7, a.disc_8, a.disc_10, a.disc_11, a.inSub FROM orders o, ( select opi.order_id, " \
          u" sum(case when opi.pay_id = 1 then opi.pay_value else 0 end) as pay_1, " \
          u" sum(case when opi.pay_id = 2 then opi.pay_value else 0 end) as pay_2, " \
          u" sum(case when opi.pay_id = 3 then opi.pay_value else 0 end) as pay_3, " \
          u" sum(case when opi.pay_id = 4 then opi.pay_value else 0 end) as pay_4, " \
          u" sum(case when opi.pay_id = 5 then opi.pay_value else 0 end) as pay_5, " \
          u" sum(case when opi.pay_id = 6 then opi.pay_value else 0 end) as pay_6, " \
          u" sum(case when opi.pay_id = 6 then opi.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_6, " \
          u" sum(case when opi.pay_id = 7 then opi.pay_value else 0 end) as pay_7, " \
          u" sum(case when opi.pay_id = 7 then opi.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_7, " \
          u" sum(case when opi.pay_id = 8 then opi.pay_value else 0 end) as pay_8, " \
          u" sum(case when opi.pay_id = 8 then opi.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_8, " \
          u" sum(case when opi.pay_id = 9 then opi.pay_value else 0 end) as pay_9, " \
          u" sum(case when opi.pay_id = 10 then opi.pay_value else 0 end) as pay_10, " \
          u" sum(case when opi.pay_id = 10 then opi.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_10, " \
          u" sum(case when opi.pay_id = 11 then opi.pay_value else 0 end) as pay_11, " \
          u" sum(case when opi.pay_id = 11 then opi.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_11, " \
          u" sum(opi.pay_value) as inSub from order_payment_info opi, payment p where opi.pay_id = p.id group by opi.order_id ) as a  " \
          u" WHERE o.order_sn = a.order_id  " \
          u" and o.add_time>='{start_a}' " \
          u" and o.add_time<='{end_a}' " \
          u" and o.shop_code ='{shopcode_a}' " \
          u" UNION all SELECT DATE_FORMAT( occ.add_time, '%Y-%m-%d'), occ.disc, occ.disc_cash, " \
          u" occ.disc - occ.disc_cash, b.pay_1, b.pay_2, b.pay_3, b.pay_4, b.pay_5, b.pay_6, " \
          u" b.pay_7, b.pay_8, b.pay_9, b.pay_10, b.pay_11, b.disc_6, b.disc_7, b.disc_8, b.disc_10, b.disc_11, " \
          u" b.inSub FROM order_change_card occ, (select occp.order_id, " \
          u" sum(case when occp.pay_id = 1 then occp.pay_value else 0 end) as pay_1, " \
          u" sum(case when occp.pay_id = 2 then occp.pay_value else 0 end) as pay_2, " \
          u" sum(case when occp.pay_id = 3 then occp.pay_value else 0 end) as pay_3, " \
          u" sum(case when occp.pay_id = 4 then occp.pay_value else 0 end) as pay_4, " \
          u" sum(case when occp.pay_id = 5 then occp.pay_value else 0 end) as pay_5, " \
          u" sum(case when occp.pay_id = 6 then occp.pay_value else 0 end) as pay_6, " \
          u" sum(case when occp.pay_id = 6 then occp.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_6, " \
          u" sum(case when occp.pay_id = 7 then occp.pay_value else 0 end) as pay_7, " \
          u" sum(case when occp.pay_id = 7 then occp.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_7, " \
          u" sum(case when occp.pay_id = 8 then occp.pay_value else 0 end) as pay_8, " \
          u" sum(case when occp.pay_id = 8 then occp.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_8, " \
          u" sum(case when occp.pay_id = 9 then occp.pay_value else 0 end) as pay_9, " \
          u" sum(case when occp.pay_id = 10 then occp.pay_value else 0 end) as pay_10, " \
          u" sum(case when occp.pay_id = 10 then occp.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_10, " \
          u" sum(case when occp.pay_id = 11 then occp.pay_value else 0 end) as pay_11, " \
          u" sum(case when occp.pay_id = 11 then occp.pay_value * case when p.dis_rate is not null then p.dis_rate else 0 end else 0 end) as disc_11, " \
          u" sum(occp.pay_value) as inSub from order_change_card_payment occp, payment p  " \
          u" where occp.pay_id = p.id group by occp.order_id ) as b " \
          u" WHERE occ.order_sn = b.order_id " \
          u" and occ.add_time>='{start_b}' " \
          u" and occ.add_time<='{end_b}' " \
          u" and occ.shop_code ='{shopcode_b}'  " \
          u" UNION all SELECT DATE_FORMAT( ouc.add_time, '%Y-%m-%d'), 0, 0, " \
          u" 0, ouc.diff_price, 0, 0, 0, 0, 0, " \
          u" 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, " \
          u" 0 FROM order_up_card ouc " \
          u" WHERE ouc.add_time>='{start_b}' " \
          u" and ouc.add_time<='{end_b}' " \
          u" and ouc.shop_code ='{shopcode_b}' ) d group by  d.date_time " \
        .format(start_a=start, end_a=endTime, shopcode_a=shopcode, start_b=start, end_b=endTime,shopcode_b=shopcode)
    cur.execute(sql)
    List = cur.fetchall()

    # 表单分页开始
    paginator = Paginator(List, 31)

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
    return render(request, 'report/card/saleGroupByShop/DateDetail.html', locals())