# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/3/21 14:51'

from django.conf.urls import url

urlpatterns = [
    url(r'^allocate/$', 'sellcard.fornt.consign.allocate.index', name='allocate_card'),
    url(r'^allocate/detail/$', 'sellcard.fornt.consign.allocate.detail', name='allocate_detail'),
    url(r'^allocate/save/$', 'sellcard.fornt.consign.allocate.save', name='allocate_save'),
]