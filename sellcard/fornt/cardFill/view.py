#-*- coding:utf-8 -*-
from django.shortcuts import render

def index(reauest):

    return render(reauest,'cardFill.html',locals())

def query(reauest):

    return render(reauest,'cardFillQuery.html',locals())
