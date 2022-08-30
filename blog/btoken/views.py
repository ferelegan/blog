import hashlib
import json
import time

import jwt
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from user.models import UserProfile


class TokenView(View):
    def get(self,request):
        return HttpResponse('<h1>from tokens model</h1>')

    def post(self,request):
        json_str = request.body
        py_obj = json.loads(json_str)

        username = py_obj['username']
        password = py_obj['password']

        try:
            user = UserProfile.objects.get(username = username)
        except:
            return JsonResponse({'code':306,'error':'用户名或密码错误'})

        # 密码验证
        md5 = hashlib.md5()
        md5.update(password.encode())
        password = md5.hexdigest()
        if password != user.password:
            return JsonResponse({'code':306,'error':'用户名或密码错误'})

        token = get_token(user.username) # type:bytes
        token = token.decode() # type:str

        return JsonResponse({'code':200,'username':user.username,'data':{'token':token}})

def get_token(username,expire=3600*24) -> bytes:
    exp = time.time() + expire
    payload = {'username':username,'exp':exp}
    return jwt.encode(payload,settings.JWT_TOKEN_KEY)