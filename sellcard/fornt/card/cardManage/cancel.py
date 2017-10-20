# -*-  coding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
import json, datetime

from sellcard.common.model import MyError
from sellcard.common import Method as mth
from sellcard.models import CardInventory


def index(request):
    operator = request.session.get('s_uid', '')
    shopcode = request.session.get('s_shopcode', '')
    roleid = request.session.get("s_roleid", '')
    rates = request.session.get('s_rates')

    # 在服务端session中添加key认证，避免用户重复提交表单
    token = 'allow'  # 可以采用随机数
    request.session['postToken'] = token
    card_no = request.POST.get('card_no', '')
    if card_no is None:
        card_no = ''
    if card_no != '':
        data_info = CardInventory.objects.values('card_blance', 'shop_code').filter(card_no=card_no)
        if data_info is None or len(data_info) == 0:
            msg = 1
        elif data_info[0]['shop_code'] != shopcode:
            msg = 2
        else:
            msg = 3

    return render(request, 'card/manage/cancel.html', locals())


def save(request):
    u_name = request.session.get('s_unameChinese')
    s_uid = request.session.get('s_uid')
    # 检测session中Token值，判断用户提交动作是否合法
    Token = request.session.get('postToken', default=None)
    # 获取用户表单提交的Token值
    userToken = request.POST.get('postToken', '')
    if userToken != Token:
        raise MyError('重复提交，刷新页面后，重试！')

    card_no = request.POST.get('card_no')
    res = {}
    conn = mth.getMysqlConn()
    cur = conn.cursor()
    try:
        conn.autocommit(False)

        sql = u" insert into card_inventory_delete( " \
              u" card_no,card_value,card_status,card_action,card_addtime,shop_code, " \
              u" card_blance,charge_time,order_sn,sheetid,is_store,username, " \
              u" delete_time,delete_user_id,delete_user_name)" \
              u" select ci.card_no,ci.card_value,ci.card_status,ci.card_action,ci.card_addtime,ci.shop_code," \
              u" ci.card_blance,ci.charge_time,ci.order_sn,ci.sheetid,ci.is_store,ci.username,now(), " \
              u" '{s_uid}', " \
              u" '{u_name}' " \
              u" from card_inventory ci " \
              u" WHERE ci.card_no = '{card_no}'".format(s_uid=s_uid,u_name=u_name,card_no=card_no)
        cur.execute(sql)
        sql = u"delete from card_inventory WHERE card_no = '{card_no}'".format(card_no=card_no)
        cur.execute(sql)
        conn.commit()
        res['status'] = 1
        del request.session['postToken']
    except Exception as e:
        conn.rollback()
        res['status'] = 0
        if hasattr(e, 'value'):
            res['msg'] = e.value
    finally:
        cur.close()
        conn.close()
        return HttpResponse(json.dumps(res))
