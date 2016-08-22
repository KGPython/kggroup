#-*- coding:utf-8 -*-
__author__ = 'liubf'

import json,datetime
from io import BytesIO

from django.db import connection
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import decimal
from sellcard.models import AdminUser,DiscountRate
from sellcard.common import Method as mtu,Constants as cts


def index(request):

    return render(request, "login.html")

#登录
@csrf_exempt
def login(request):
    user_name = mtu.getReqVal(request,"user_name","")
    password = mtu.getReqVal(request,"password","")
    vcode = mtu.getReqVal(request,"vcode","")
    try:
        vcode2 = request.session["s_vcode"]
    except:
        vcode2 = ""

    response_data = {}
    try:
        if vcode == vcode2:
            # 查询用户信息
            user = AdminUser.objects.get(user_name=user_name)
            upwd = user.password
            password = mtu.md5(password)
            shop_code=user.shop_code
            rates = DiscountRate.objects.values('val_min','val_max','discount_rate').filter(shopcode=shop_code)
            rateList=[]
            for rate in rates:
                item={}
                item['val_min']=float(rate['val_min'])
                item['val_max']=float(rate['val_max'])
                item['discount_rate']=float(rate['discount_rate'])
                rateList.append(item)

            if upwd == password:
                request.session["s_uname"] = user.user_name
                request.session["s_unameChinese"] = user.name
                request.session["s_roleid"] = user.role_id
                request.session["s_shopid"] = user.shop_id
                request.session["s_shopcode"] = user.shop_code
                request.session["s_depart"] = user.depart
                request.session["s_uid"] = user.id
                request.session["s_rates"] = rateList
                if user.role_id in ["2","3","5"]:
                    #售卡前台
                    response_data['homeurl'] = cts.URL_HOME[1]
                else:
                    # 售卡后台
                    response_data['homeurl'] = cts.URL_HOME[0]

                request.session["homeurl"] = response_data['homeurl']

                # 查询菜单权限
                purlist = findNavByRcode(user.role_id)
                request.session["s_umenu"] = getMenu(purlist)
                response_data['status'] = "0"
            else:
                response_data['status'] = "2"
        else:
            response_data['status'] = "3"
    except Exception as e:
        print(e)
        response_data['status'] = "1"

    return HttpResponse(json.dumps(response_data), content_type="application/json")

def getMenu(purlist):
    m1list = sorted(purlist, key=lambda pur: pur["nav_id"])
    menu_dict = {}
    if m1list:
        for p in m1list:
            if p["parent_id"]=='-1':
                p.setdefault("sub",[])
                menu_dict.setdefault("nav_"+str(p["nav_id"]),p)
            else:
                pid = str(p["parent_id"])
                if "nav_"+pid in menu_dict and "sub" in menu_dict["nav_"+pid]:
                    menu_dict["nav_"+pid]["sub"].append(p)
    menu_list = [item for item in menu_dict.values()]

    menu_list = sorted(menu_list, key=lambda menu: menu["sort_id"])
    return menu_list


#根据角色编码查询菜单
def findNavByRcode(rcodes):

    sql = "select DISTINCT r.role_id,r.nav_id, "
    sql += "n.nav_name,n.parent_id,n.url, "
    sql += "n.sort_id,n.icon "
    sql += "from role_nav r,nav_list n "
    sql += "where r.nav_id=n.nav_id "
    sql += "and n.flag=0 "
    if rcodes:
        sql += "and r.role_id in (" + rcodes + ") "

    sql += "order by n.sort_id "

    cursor = connection.cursor()
    cursor.execute(sql)
    plist = cursor.fetchall()
    rslist = []
    if plist:
        for p in plist:
            item = []
            item.append(("role_id",p[0]))
            item.append(("nav_id",p[1]))
            item.append(("nav_name",p[2]))
            item.append(("parent_id",p[3]))
            item.append(("url",p[4]))
            item.append(("sort_id",p[5]))
            item.append(("icon",p[6]))
            rslist.append(dict(item))
    return rslist


#验证码
def vcode(request):
    image = mtu.verifycode(request,'s_vcode')
    #将image信息保存到BytesIO流中
    buff = BytesIO()
    image.save(buff,"png")
    return HttpResponse(buff.getvalue(),'image/png')

#注销
def logout(request):
    try:
        del request.session["s_uname"]
        del request.session["s_roleid"]
        del request.session["s_vcode"]
        del request.session["s_umenu"]
        del request.session["homeurl"]
    except:
        print("session[s_uname]不存在")

    return render(request,"login.html")

@csrf_exempt
def updatePwd(request):
    data = {}
    if request.method == 'POST':

        userId =request.session["s_uid"]
        try:
            newPwd = mtu.getReqVal(request,"newPwd","")
            pwd = mtu.md5(newPwd)
            AdminUser.objects.filter(id=userId).update(password=pwd)
            data["result"] = "0"
        except Exception as e:
            print(e)

    return render(request,'restPassword.html',locals())

