from django.shortcuts import render

def index(request):

    return render(request, "index.html")

def global_setting(request):
    # 加密狗验证服务地址
    SOFTKEY_URL = "http://192.168.250.8:8082/authservice/inf/main"
    return locals()