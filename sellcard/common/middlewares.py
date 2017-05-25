#-*- coding:utf-8 -*-
__author__ = 'liubf'

from django.conf import settings
import re
from django.http import HttpResponseRedirect as redirect

EXEMPT_URLS=[re.compile(settings.KGGROUP_LOGIN_URL.lstrip('/'))]

if hasattr(settings,'KGGROUP_LOGIN_EXEMPT_URLS'):
	EXEMPT_URLS += [re.compile(expr) for expr in settings.KGGROUP_LOGIN_EXEMPT_URLS]

class KgLoginMiddleware(object):
    def process_request(self, request):
        #此用户没有登陆，判断请求的路径是否合法：
        path = request.path_info.lstrip('/')
        #不过滤css/js/image
        if path.find("css/")==-1 and path.find("js/")==-1 and path.find("images/")==-1:
            #如果用户未登录，跳转到登录页面
            if 's_uname' not in request.session or not request.session.get("s_uname",default=None):
                    if not any(m.match(path) for m in EXEMPT_URLS):
                        print(">>>>>>>>>user not logged in ，url invalid："+path)
                        return redirect(settings.KGGROUP_LOGIN_URL)
                    else:
                        print(">>>>>>>>>begin login ："+path)
            else:
                s_uname =  request.session.get("s_uname",default=None)
                STATIC_VERSION = settings.STATIC_VERSION
                request.session["s_static_version"] = STATIC_VERSION
                print(">>>>>>>>>already login, user："+s_uname,path)
        else:
            request.path_info = re.sub(r'\.v\d+', '', request.path_info)
            print(">>>>>>>>>static url not filter："+path)




