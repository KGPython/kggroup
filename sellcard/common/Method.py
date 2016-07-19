__author__ = 'admin'

import pymssql,random,hashlib
from PIL import Image, ImageDraw, ImageFont
from sellcard.common import Constants
from sellcard.models import CardInventory
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from sellcard.models import Orders
import datetime

def getMssqlConn(as_dict=True):
    conn = pymssql.connect(host=Constants.SCM_DB_SERVER,
                           port=Constants.SCM_DB_PORT,
                           user=Constants.SCM_DB_USER,
                           password=Constants.SCM_DB_PASSWORD,
                           database=Constants.SCM_DB_DATABASE,
                           charset='utf8',
                           as_dict=as_dict)
    return conn
def getReqVal(request,key,default=None):

    if request.method=="GET":
        val = request.GET.get(key,default)
    elif request.method=="POST":
        val = request.POST.get(key,default)

    return val

#md5
def md5(str):

    md5 = hashlib.md5()
    if str:
        md5.update(str.encode(encoding='utf-8'))

    return md5.hexdigest()

#������֤��
def   verifycode(request,key):
    # �����ɫ1:
    def rndColor():
        return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

    # �����ɫ2:
    def rndColor2():
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    # 240 x 60:
    width = 60 * 4
    height = 80
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # ����Font����:
    root = settings.BASE_DIR+Constants.FONT_ARIAL
    font = ImageFont.truetype(root, 80)     #36 - �����С����ֵ�������
    # ����Draw����:
    draw = ImageDraw.Draw(image)
    # ���ÿ������:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())

    # �������:
    chars=['0','1','2','3','4','5','6','7','8','9',
           #'a','b','c','d','e','f','g','h','i','j','k','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           #'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
           ]
    y = [y for y in [random.randint(x-x, len(chars)-1) for x in range(4)] ]
    charlist = [chars[i] for i in y]

    rcode = ''.join(map(str,charlist))

    for t in range(len(charlist)):
        draw.text((60 * t + 10, 3), charlist[t], font=font, fill=rndColor2())

    #����֤��ת����Сд�ģ������浽session��
    request.session[key] =rcode

    return image
def cardCheck(request):
    cardId = request.GET.get('cardId','')
    findCardById = CardInventory.objects.all().filter(card_no=cardId)
    findCardById = serializers.serialize('json',findCardById)
    return HttpResponse(findCardById,content_type="application/json")

def setOrderSn(request):
    start = datetime.date.today().strftime('%Y-%m-%d 00:00:00')
    end = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    count  = Orders.objects.filter(add_time__gte=start,add_time__lte=end).count()
    return count
