#-*- coding:utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum
import datetime

from sellcard.models import OrderUpCard
from sellcard.common import Method as mth
from sellcard import views as base
def index(request):
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
    if role_id == '9':
        shops = mth.getCityShops('T')
        shopsCode = mth.getCityShopsCode('T')
        shopsCodeStr = "'"+"','".join(shopsCode)+"'"
    if role_id == '8':
        shops = mth.getCityShops('C')
        shopsCode = mth.getCityShopsCode('C')
        shopsCodeStr = "'"+"','".join(shopsCode)+"'"

    saleDiscGroupByShop = 'select shop_code,SUM(disc_amount) as disc,SUM(y_cash) as disc_cash, SUM(disc_amount-y_cash) as disc_card ' \
                          'from orders ' \
                          'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr})' \
                          'group by shop_code ' \
                          .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(saleDiscGroupByShop)
    saleDiscList = cur.fetchall()

    salePayGroupByShop = 'select ord.shop_code,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                'from orders as ord , order_payment_info as info ' \
                'where ord.add_time>="{start}" and ord.add_time<="{end}" and shop_code in ({shopsCodeStr}) and ord.order_sn = info.order_id ' \
                'group by ord.shop_code,info.pay_id' \
                .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(salePayGroupByShop)
    salePayList = cur.fetchall()


    fillList = OrderUpCard.objects\
            .values('shop_code')\
            .filter(add_time__gte=start,add_time__lte=endTime,shop_code__in=shopsCode)\
            .annotate(fill=Sum('diff_price'))\
            .order_by('shop_code')

    changeDiscGroupByShop = 'select shop_code,SUM(disc) as disc,SUM(disc_cash) as disc_cash,(SUM(disc-disc_cash)) as disc_card ' \
                  'from order_change_card ' \
                  'where add_time>="{start}" and add_time<="{end}" and shop_code in ({shopsCodeStr}) ' \
                  'group by shop_code ' \
                  .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(changeDiscGroupByShop)
    changeDiscList = cur.fetchall()
    changePayGroupByShop = 'select ord.shop_code ,info.pay_id ,SUM(info.pay_value) as pay_value ' \
                           'from order_change_card as ord , order_change_card_payment as info ' \
                           'where ord.add_time>="{start}" and ord.add_time<="{end}" and shop_code in ({shopsCodeStr}) and ord.order_sn = info.order_id ' \
                           'group by ord.shop_code,info.pay_id' \
                           .format(start=start, end=endTime,shopsCodeStr=shopsCodeStr)
    cur.execute(changePayGroupByShop)
    changePayList = cur.fetchall()


    totalDict  = {'discTotal':0,'discCashTotal':0,'discCardTotal':0,'inSubTotal':0,'total_1':0,'total_2':0,'total_3':0,
                  'total_4':0,'total_5':0,'total_6':0,'total_7':0,'total_8':0,'total_9':0,'total_10':0,'total_11':0,}

    dataList = []
    for i in range(0,len(shops)):
        if shops[i]['shop_code'] != 'ZBTG':
            item = {'shop_code':'','disc':0,'disc_cash':0,'disc_card':0,'inSub':0,'pay_1':0,'pay_2':0,'pay_3':0,
                    'pay_4':0,'pay_5':0,'pay_6':0,'pay_7':0,'pay_8':0,'pay_9':0,'pay_10':0,'pay_11':0,}
            item['shop_code'] = shops[i]['shop_code']
            for sale in salePayList:
                if sale['shop_code']==item['shop_code']:

                    #横向各门店售卡汇总赋值
                    pay_id = sale['pay_id']
                    if sale['pay_id'] == 1:
                        item['pay_1'] += float(sale['pay_value'])
                    if sale['pay_id'] == 2:
                        item['pay_2'] += float(sale['pay_value'])
                    if sale['pay_id'] == 3:
                        item['pay_3'] += float(sale['pay_value'])
                    if sale['pay_id'] == 4:
                        item['pay_4'] += float(sale['pay_value'])
                    if sale['pay_id'] == 5:
                        item['pay_5'] += float(sale['pay_value'])
                    if sale['pay_id'] == 6:
                        item['pay_6'] += float(sale['pay_value'])
                    if sale['pay_id'] == 7:
                        item['pay_7'] += float(sale['pay_value'])
                    if sale['pay_id'] == 8:
                        item['pay_8'] += float(sale['pay_value'])
                    if sale['pay_id'] == 9:
                        item['pay_9'] += float(sale['pay_value'])
                    if sale['pay_id'] == 10:
                        item['pay_10'] += float(sale['pay_value'])
                    if sale['pay_id'] == 11:
                        item['pay_11'] += float(sale['pay_value'])

                    item['inSub'] += float(sale['pay_value'])

            for saleDisc in saleDiscList:
                if saleDisc['shop_code'] == item['shop_code']:
                    if not saleDisc['disc']:
                        saleDisc['disc'] = 0
                    if not saleDisc['disc_cash']:
                        saleDisc['disc_cash'] = 0
                    if not saleDisc['disc_card']:
                        saleDisc['disc_card'] = 0
                    item['disc'] += float(saleDisc['disc'])
                    item['disc_cash'] += float(saleDisc['disc_cash'])
                    item['disc_card'] += float(saleDisc['disc_card'])

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
                    if change['pay_id'] == 4:
                        item['pay_4'] += float(change['pay_value'])
                    if change['pay_id'] == 5:
                        item['pay_5'] += float(change['pay_value'])
                    if change['pay_id'] == 6:
                        item['pay_6'] += float(change['pay_value'])
                    if change['pay_id'] == 7:
                        item['pay_7'] += float(change['pay_value'])
                    if change['pay_id'] == 8:
                        item['pay_8'] += float(change['pay_value'])
                    if change['pay_id'] == 9:
                        item['pay_9'] += float(change['pay_value'])
                    if change['pay_id'] == 10:
                        item['pay_10'] += float(change['pay_value'])
                    if change['pay_id'] == 11:
                        item['pay_11'] += float(change['pay_value'])

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
            totalDict['discCardTotal'] += item['disc_card']
            totalDict['inSubTotal'] += item['inSub']
            totalDict['total_1'] += item['pay_1']
            totalDict['total_2'] += item['pay_2']
            totalDict['total_3'] += item['pay_3']
            totalDict['total_4'] += item['pay_4']
            totalDict['total_5'] += item['pay_5']
            totalDict['total_6'] += item['pay_6']
            totalDict['total_7'] += item['pay_7']
            totalDict['total_8'] += item['pay_8']
            totalDict['total_9'] += item['pay_9']
            totalDict['total_10'] += item['pay_10']
            totalDict['total_11'] += item['pay_11']

            dataList.append(item)
    return render(request, 'report/saleGroupByShop.html', locals())


def detail(request):
    today = datetime.date.today()
    page = mth.getReqVal(request, 'page', 1)
    shop_code = request.GET.get('shop_code')
    pay_id = request.GET.get('pay_id')

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

    paginator = Paginator(List, 20)

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
    return render(request, 'report/saleGroupByShop/Detail.html', locals())
