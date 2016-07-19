#-*- coding:utf-8 -*-
__author__ = 'liubf'
from django.shortcuts import render

def index(request):

    return render(request, "admin/index.html")