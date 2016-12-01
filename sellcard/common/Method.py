#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
import pymssql,random,hashlib
from PIL import Image, ImageDraw, ImageFont
from sellcard.common import Constants
from sellcard.models import CardInventory, Orders, OrderChangeCard, OrderUpCard, ExchangeCode, OrderPaymentInfo, \
    OrderInfo, DisCode, OrderUpCardInfo, OrderChangeCardInfo
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
import datetime,json
import pymysql,_mssql
import decimal
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count


def getMssqlConn(as_dict=True):
    conn = pymssql.connect(host=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8',
                           as_dict=as_dict)
    return conn


def get_MssqlConn():
    conn = _mssql.connect(server=Constants.KGGROUP_DB_SERVER,
                           port=Constants.KGGROUP_DB_PORT,
                           user=Constants.KGGROUP_DB_USER,
                           password=Constants.KGGROUP_DB_PASSWORD,
                           database=Constants.KGGROUP_DB_DATABASE,
                           charset='utf8')
    return conn


def getReqVal(request, key, default=None):
    key = key.strip()

    if request.method == "GET":
        val = request.GET.get(key, default)
    elif request.method == "POST":
        val = request.POST.get(key, default)

    return val


# md5
def md5(str):
    md5 = hashlib.md5()
    if str:
        md5.update(str.encode(encoding='utf-8'))

    return md5.hexdigest()

#生成验证码
def  verifycode(request,key):
    # 随机颜色1:
    def rndColor():
        return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

    # 随机颜色2:
    def rndColor2():
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    # 240 x 60:
    width = 60 * 4
    height = 80
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    root = settings.BASE_DIR + Constants.FONT_ARIAL
    font = ImageFont.truetype(root, 80)  # 36 - 字体大小，数值大字体大
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())

    # 输出文字:
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             # 'a','b','c','d','e','f','g','h','i','j','k','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
             # 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
             ]
    y = [y for y in [random.randint(x - x, len(chars) - 1) for x in range(4)]]
    charlist = [chars[i] for i in y]

    rcode = ''.join(map(str, charlist))

    for t in range(len(charlist)):
        draw.text((60 * t + 10, 3), charlist[t], font=font, fill=rndColor2())

    # 将验证码转换成小写的，并保存到session中
    request.session[key] = rcode

    return image





# 折扣修改授权码校验
def disCodeCheck(request):
    disCode = request.GET.get('discode', '')
    disCodeList = DisCode.objects.values('flag').filter(dis_code=disCode)
    res = {}
    if disCodeList and disCodeList[0]['flag'] == '':
        res['msg'] = '0'
    else:
        res['msg'] = '1'
    return HttpResponse(json.dumps(res), content_type="application/json")


def updateDisCode(id, shop, orderSn):
    res = 0
    try:
        res = DisCode.objects.filter(dis_code=id).update(flag='1', change_time=datetime.datetime.now(),order_sn=orderSn,shopcode=shop)
    except Exception as e:
        print(e)
    return res



# 充值卡卡校验
def cardCheck(request):
    cardId = request.GET.get('cardId','')
    tempList = cardId.split('=')
    if len(tempList)>0:
        cardId = (tempList[0])
    cardId =cardId.strip()
    findCardById = CardInventory.objects.all().filter(card_no=cardId)
    findCardById = serializers.serialize('json',findCardById)
    return HttpResponse(findCardById,content_type="application/json")


# 换卡,充值卡校验
def cardCheck_Change(request):
    #查询erp内部卡信息
    cardId = request.GET.get('cardId', '')
    cardId = cardId.strip()
    conn = getMssqlConn()
    cursor = conn.cursor()
    sql = "select New_amount, detail, mode from guest where CardNO='{cardId}'".format(cardId=cardId)
    cursor.execute(sql)
    data = cursor.fetchone()
    data['New_amount'] = float(data['New_amount'])
    data['detail'] = float(data['detail'])

    #查询mysql内部卡信息


    return HttpResponse(json.dumps(data), content_type="application/json")
def cardCheck_Mssql(request):
    cardId = request.GET.get('cardId', '')
    # cardId='501410070'
    item = {}
    item.setdefault("card_no", cardId)
    try:
        conn = getMssqlConn()
        cur = conn.cursor()
        sql = "select cardno,cardtype,sheetid,mode,detail,memo " \
              "from guest where cardno='{cardId}'".format(cardId=cardId)
        cur.execute(sql)
        item1 = cur.fetchone()

        if item1:
            sql = "select sheetid,cardtype,money,amount from batchsalecarditem " \
                  "where cast(beginno as bigint)<={cardId} and cast(endno as bigint)>={cardId} ".format(cardId=cardId)
            cur.execute(sql)
            item2 = cur.fetchone()

            item.setdefault("card_value", str(item2["money"]))
            item.setdefault("card_blance", str(item1["detail"]))
            item.setdefault("card_status", str(item1["mode"]))
        else:
            item.setdefault("card_value", '0.0')
            item.setdefault("card_blance", '0.0')
            item.setdefault("card_status", "-1")
    except Exception as e:
        print(e)
        item.setdefault("card_value", '0.0')
        item.setdefault("card_blance", '0.0')
        item.setdefault("card_status", "-1")

    return HttpResponse(json.dumps(item), content_type="application/json")

# 黄金手--兑换码状态更新
def upChangeCode(list, shopcode):
    ExchangeCode.objects.filter(code__in=list).update(shop_code=shopcode, exchange_time=datetime.datetime.now())
    return True


# 黄金手--兑换码校验
@csrf_exempt
def changeCodeCheck(request):
    code = (request.POST.get('code', '')).strip()
    camilo = (request.POST.get('camilo', '')).strip()
    res = ExchangeCode.objects.filter(code=code, camilo=camilo).values('cost', 'shop_code')
    data = {}
    if len(res) > 0:
        data['cost'] = str(res[0]['cost'])
        data['shop_code'] = res[0]['shop_code']

    return HttpResponse(json.dumps(data), content_type="application/json")


# 跟新ERP内部卡状态
def updateCard(list, mode):
    cards = "'"
    for obj in list:
        cards += str(obj)
        cards += "','"
    cards = cards[0:len(cards) - 2]
    sql = "UPDATE guest SET Mode ='" + mode + "' WHERE CardNO in (" + cards + ")"
    conn = getMssqlConn()
    conn.autocommit(False)
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    return res


# 更新赊销状态
@csrf_exempt
def upNoPayStatus(request):
    orderSn = request.POST.get('orderSn')
    dateStr = request.POST.get('date')
    date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
    res = {}
    try:
        OrderPaymentInfo.objects.filter(order_id=orderSn, pay_id=4).update(is_pay='1', change_time=date)
        res['msg'] = '0'
    except Exception as e:
        print(e)
        res['msg'] = '1'
    return HttpResponse(json.dumps(res))


def setOrderSn(mode=None):
    start = datetime.date.today().strftime('%Y-%m-%d 00:00:00')
    end = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    count = 0
    if mode:
        count = mode.objects.filter(add_time__gte=start, add_time__lte=end).count() + 1
    else:
        count = Orders.objects.filter(add_time__gte=start, add_time__lte=end).count() + 1
    if count < 10:
        sn = datetime.date.today().strftime('%y%m%d') + '000' + str(count)
    elif count >= 10 and count < 100:
        sn = datetime.date.today().strftime('%y%m%d') + '00' + str(count)
    elif count >= 100 and count < 1000:
        sn = datetime.date.today().strftime('%y%m%d') + '0' + str(count)
    elif count >= 1000 and count < 10000:
        sn = datetime.date.today().strftime('%y%m%d') + str(count)
    return sn


# 获取mysql数据库连接
def getMysqlConn():
    conn = pymysql.connect(host=Constants.SCM_DB_MYSQL_SERVER,
                           port=Constants.SCM_DB_MYSQL_PORT,
                           user=Constants.SCM_DB_MYSQL_USER,
                           password=Constants.SCM_DB_MYSQL_PASSWORD,
                           db=Constants.SCM_DB_MYSQL_DATABASE,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


def convertToStr(val, *arg):
    if arg:
        fmt, divisor = arg[0], arg[1]
    else:
        fmt, divisor = None, None

    if not fmt:
        fmt = "0.00"
    if not divisor:
        divisor = 10000

    if isinstance(val, decimal.Decimal):
        return str(float((val / divisor).quantize(decimal.Decimal(str(fmt)))))
    else:
        if val:
            return str(float(val))
        else:
            return "0.00"


def orderDetail(request):
    orderSn = request.GET.get('orderSn', '')
    actionType = request.GET.get('actionType', '1')
    if actionType == '1':
        order = Orders.objects \
            .values('order_sn', 'shop_code', 'paid_amount', 'disc_amount', 'action_type', 'buyer_name', 'buyer_tel',
                    'buyer_company', 'add_time', 'remark') \
            .filter(order_sn=orderSn)
        orderInfo = OrderInfo.objects.values('card_id', 'card_balance').filter(order_id=orderSn)
        orderPayInfo = OrderPaymentInfo.objects.values('pay_id', 'pay_value', 'remarks').filter(order_id=orderSn)
        cardsNum = OrderInfo.objects.filter(order_id=orderSn).count()
    elif actionType == '2':
        order = OrderUpCard.objects \
            .values('order_sn', 'shop_code', 'action_type', 'total_amount', 'total_price', 'fill_amount', 'fill_price',
                    'diff_price', 'state', 'user_name', 'user_phone') \
            .filter(order_sn=orderSn)
        # 丢失卡
        orderInfo = OrderUpCardInfo.objects.values('card_no', 'card_value', 'card_balance', 'card_attr').filter(order_sn=orderSn)
        cardsNum = OrderUpCardInfo.objects.filter(order_sn=orderSn).count()
    elif actionType == '3':
        order = OrderChangeCard.objects \
            .values('shop_code', 'depart', 'operator_id', 'order_sn', 'total_in_price', 'total_in_amount',
                    'total_out_price', 'total_out_amount', 'add_time') \
            .filter(order_sn=orderSn)
        orderInfo = OrderChangeCardInfo.objects.values('card_no', 'card_attr', 'card_value', 'card_balance') \
            .filter(order_sn=orderSn)
        # cardsNum = OrderChangeCardInfo.objects.values('card_attr', 'card_no') \
        #   .filter(order_sn=orderSn) \
        #   .annotate(total=Count('card_no')) \
        #   .order_by('card_attr')
        cardsNum = OrderChangeCardInfo.objects.values('card_attr', 'card_no', 'card_value', 'card_balance'). \
            filter(order_sn=orderSn)
        cardsInNum = 0
        cardsOutNum = 0
        for num in cardsNum:
            if num['card_attr'] == '1':
                cardsInNum += 1
            if num['card_attr'] == '0':
                cardsOutNum += 1
    return render(request, 'orderDetail.html', locals())



