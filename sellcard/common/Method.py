#-*- coding:utf-8 -*-
__author__ = 'admin'
from django.shortcuts import render
import pymssql,random,hashlib
from PIL import Image, ImageDraw, ImageFont
from sellcard.common import Constants
from sellcard.models import CardInventory, Orders, ExchangeCode,DisCode,Shops,Payment
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
import datetime,json
import pymysql,_mssql
import decimal
from sellcard.common.model import MyError

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
    if data:
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

def updateCard(updateConfList):
    conn = getMssqlConn()
    cur = conn.cursor()
    res = {}
    try:
        conn.autocommit(False)
        for conf in updateConfList:
            mode = conf['mode']
            if mode in ('9','7'):
                cardStatus = '1'
            elif mode == '1':
                cardStatus = '9'

            cards = "'"+"','".join(conf['ids'])+"'"
            sql = "UPDATE guest SET Mode ='{mode}' WHERE CardNO IN ({cards}) AND detail=new_amount AND mode={cardStatus} "\
                .format(mode=mode,cards=cards,cardStatus=cardStatus)
            cur.execute(sql)
            updateNum = cur.rowcount
            if updateNum != conf['count'] :
                raise MyError('Guest中：'+cards+'状态更新失败')
        conn.commit()
        res['status'] = 1
    except Exception as e:
        conn.rollback()
        res["status"] = 0
        if hasattr(e, 'value'):
            res['msg'] = e.value
    finally:
        cur.close()
        conn.close()
        return res


    # try:
    #     conn.autocommit(False)
    #     cur.execute(sql)
    #     res = cur.rowcount
    #     if res != num :
    #         raise MyError('卡库数据更新失败')
    #     else:
    #         conn.commit()
    #         return type
    # except Exception as e:
    #     conn.rollback()
    #     print(e)
    #     return False
    # finally:
    #     cur.close()
    #     conn.close()


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




def getCityShops(city=None):
    kwargs = {}
    if city:
        kwargs.setdefault('city',city)
    shops = Shops.objects.values('shop_code','shop_name').filter(**kwargs)
    return shops

def getCityShopsCode(city=None):
    kwargs = {}
    if city:
        kwargs.setdefault('city', city)
    shops = Shops.objects.values('shop_code').filter(**kwargs).exclude(shop_code='ZBTG')
    shopsCode = [shop['shop_code'] for shop in shops]
    return shopsCode


def getPayDiscDict():
    payDisc = Payment.objects.values('id', 'dis_rate').filter(flag=0)
    payDiscDict = {str(pay['id']): pay['dis_rate'] for pay in payDisc if pay['dis_rate']}
    return payDiscDict

