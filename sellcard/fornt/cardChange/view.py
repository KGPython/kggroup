__author__ = 'admin'
from django.shortcuts import render

def index(reauest):
    return render(reauest,'cardChange.html',locals())