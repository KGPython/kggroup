__author__ = 'admin'
from django.shortcuts import render

def index(reauest):
    return render(reauest,'bulkSale.html',locals())

def queryFill(reauest):
    return render(reauest,'cardFillQuery.html',locals())