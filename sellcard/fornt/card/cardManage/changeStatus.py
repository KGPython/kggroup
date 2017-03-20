# -*-  coding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
import json,datetime

from sellcard.common.model import MyError
from sellcard.common import Method as mth
from sellcard.models import ActionLog

def statusTo1(request):
    if request.method == 'GET':
        operator = request.session.get('s_uid', '')
        shopcode = request.session.get('s_shopcode', '')
        roleid = request.session.get("s_roleid", '')
        rates = request.session.get('s_rates')

        # 在服务端session中添加key认证，避免用户重复提交表单
        token = 'allow'  # 可以采用随机数
        request.session['postToken'] = token
        return render(request, 'card/manage/changeStatus.html', locals())

    if request.method == 'POST':
        u_name = request.session.get('s_uname')
        # 检测session中Token值，判断用户提交动作是否合法
        Token = request.session.get('postToken', default=None)
        # 获取用户表单提交的Token值
        userToken = request.POST.get('postToken', '')
        if userToken != Token:
            raise MyError('表单重复提交，刷新页面后，重试！')

        cardList = request.POST.get('cardList')
        cardList = json.loads(cardList)
        cardCount = len(cardList)
        cardList = "'"+"','".join(cardList)+"'"
        cardList.replace('"',"'")
        res = {}
        conn = mth.getMssqlConn()
        cur = conn.cursor()
        try:
            conn.autocommit(False)
            sql = "UPDATE Guest SET mode = 1 WHERE cardno in ("+cardList+") AND detail=new_amount AND mode=7"
            cur.execute(sql)
            resUpdate = cur.rowcount
            if resUpdate != cardCount:
                raise MyError('更新失败。原因：更新数据条数与提交数据不符！')
            conn.commit()
            res['status'] = 1
            ActionLog.objects.create(
                action='挂售卡激活', u_name=u_name,cards_in=json.dumps(cardList),
                add_time=datetime.datetime.now()
            )
            del request.session['postToken']
        except Exception as e:
            conn.rollback()
            res['status'] = 0
            if hasattr(e,'value'):
                res['msg'] = e.value
            ActionLog.objects.create(
                action='挂售卡激活', u_name=u_name,cards_in=json.dumps(cardList),add_time=datetime.datetime.now(), err_msg=e
            )
        finally:
            cur.close()
            conn.close()
            return HttpResponse(json.dumps(res))
