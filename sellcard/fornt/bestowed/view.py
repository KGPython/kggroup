__author__ = 'admin'
from django.shortcuts import render

def index(reauest):
    return render(reauest,'bestowed.html',locals())
