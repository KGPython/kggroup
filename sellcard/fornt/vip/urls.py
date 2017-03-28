# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/21 14:51'

from django.conf.urls import url

urlpatterns = [
    url(r'^manage/', 'sellcard.fornt.vip.manage.index', name='vip_manage'),
    url(r'^manage/detail', 'sellcard.fornt.vip.manage.detail', name='vip_manage_detail'),
    url(r'^manage/save', 'sellcard.fornt.vip.manage.save', name='vip_manage_save'),
    url(r'^manage/delete', 'sellcard.fornt.vip.manage.delete', name='vip_manage_delete'),
    url(r'^sale/$','sellcard.fornt.vip.sale.index',name='vip_sale'),
    url(r'^settlement/$','sellcard.fornt.vip.settlement.index',name='vip_settlement'),
    url(r'^settlement/save$','sellcard.fornt.vip.settlement.save',name='vip_settlement_save'),
]