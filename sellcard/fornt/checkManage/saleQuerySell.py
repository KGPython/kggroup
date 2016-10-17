#-*- coding:utf-8 -*-
#齐旭
#2016-10-17

#引用框架
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
#引用系统
import datetime
#引用自身项目
from sellcard.common import Method as mth
from sellcard.models import Orders,OrderUpCard,OrderChangeCard,Shops,Departs

@csrf_exempt
def index(request):
    #GET:数据展示
    shopcode = request.session.get('s_shopcode') #门店编码
    depart_id = request.session.get('s_depart') #部门编码
    user_id = request.session.get('s_uid') #当前用户ID
    name = request.session.get('s_unameChinese') #当前用户名

    shop = Shops.objects.values('shop_name').filter(shop_code=shopcode)[0]['shop_name'] #门店名称
    depart = Departs.objects.values('depart_name').filter(depart_id=depart_id)[0]['depart_name'] #部门名称
    today = str(datetime.date.today()) #当前日期 用于显示
    resList=[] #创建集合用于记录查询结果

    #接收post查询
    actionType = mth.getReqVal(request,'actionType','1') #交易类型：1售卡、2补卡、3换卡
    start = mth.getReqVal(request,'start',today) #开始日期
    end = mth.getReqVal(request,'end',today) #结束日期
    endTime = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(1) #转换结束日期格式用于查询

    page = mth.getReqVal(request,'page',1)

    #创建查询条件字典
    kwargs = {}
    kwargs.setdefault('operator_id',user_id)
    kwargs.setdefault('shop_code',shopcode)
    kwargs.setdefault('depart',depart_id)
    kwargs.setdefault('add_time__gte',start)
    kwargs.setdefault('add_time__lte',endTime)

    #根据不同条件查询不同的集合：1售卡、2补卡、3换卡
    if actionType=='1':
        resList = Orders.objects.values('shop_code','depart','operator_id','order_sn','action_type','paid_amount','disc_amount','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')
    elif actionType=='2':
        resList = OrderUpCard.objects.values('shop_code','depart','operator_id','order_sn','diff_price','user_name','user_phone','modified_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')
    elif actionType=='3':
        resList = OrderChangeCard.objects.values('shop_code','depart','operator_id','order_sn','total_in_price','total_out_price','add_time')\
                .filter(**kwargs)\
                .order_by('shop_code','depart','operator_id')

    #嵌套分页操作
    paginator = Paginator(resList,20)
    try:
        resList = paginator.page(page)
    except Exception as e:
        print(e)

    #返回显示前台页面
    return render(request, 'saleQuerySell.html', locals())

