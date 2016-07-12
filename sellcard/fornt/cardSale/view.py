#-*- coding:utf-8 -*-
from django.shortcuts import render
def index(reauest):
    return render(reauest,'cardSale.html',locals())