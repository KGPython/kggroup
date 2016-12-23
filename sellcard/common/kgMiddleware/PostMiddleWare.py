from django.core.cache import cache
from django.http import HttpResponse
import json

class PreventRepeatPost(object):
    def process_request(self,request):
        if request.method == 'POST':
            u_id = request.session.get('s_uid','')
            key = 'sumbit_%s' % u_id
            cache.set(key, True, timeout=10)
            res = {}
            if not cache.get(key):
                res["msg"] = '10秒内不能重复提交，谢谢。'
                return HttpResponse(json.dumps(res))

