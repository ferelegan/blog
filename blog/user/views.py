import hashlib
import json
import random
import time

import jwt
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from .tasks import send_auth_code

# Create your views here.
from tools.sms import YunTongXin
from user.models import UserProfile
from django.core.cache import cache

# 生成token
def get_token(username,expire=3600*24)->bytes:
    exp = time.time()+expire
    payload = {'username':username,'exp':exp}
    return jwt.encode(payload=payload,key=settings.JWT_TOKEN_KEY)

class UserView(View):
    def get(self,request,username=None):
        try:
            user = UserProfile.objects.get(username=username)
        except:
            return JsonResponse({'code': 305, 'error': '查无此人'})

        keys = request.GET.keys()
        if keys: # 根据查询字符串取属性值，按需获取
            data = {}
            for key in keys:
                if hasattr(user,key): # python的反射，user对象中有key变量所指向的属性，则返回True
                    data[key] = getattr(user,key) # 返回user对象的key变量所指向的属性值。
            return JsonResponse({'code':200,'username':username,'data':data})
        else: #　如果查询字符串为空，则获取所有属性
            info = user.info
            sign = user.sign
            avatar = str(user.avatar) # user.avatar:会直接将图片数据返回，加上str会返回图片路径
            nickname = user.nickname
            return JsonResponse({'code': 200, 'username': username, 'data': {
                'nickname': nickname, 'info': info, 'sign': sign, 'avatar': avatar
            }})

    def post(self,request):
        # 接收前端的数据
        json_str = request.body
        py_obj = json.loads(json_str)

        username = py_obj['username']
        email = py_obj['email']
        password_1 = py_obj['password_1']
        password_2 = py_obj['password_2']
        phone = py_obj['phone']
        sms_num = py_obj['sms_num']

        # 进行数据校验
        if password_1 != password_2:
            return JsonResponse({'code':301,'error':'密码不一致'})
        password = password_2
        if not username or not password:
            return JsonResponse({'code':302,'error':'用户名或密码不能为空'})

        md5 = hashlib.md5()
        md5.update(password.encode())
        password = md5.hexdigest()

        # 短信验证码校验
        code = cache.get(f'sms_{phone}')
        print('***********code in views:%s**********'%code)
        print(type(sms_num),type(code)) # str,int
        if code != int(sms_num): # 注意类型的转换
            return JsonResponse({'code':303,'error':'验证码有误，请重新输入'})

        # 数据入库
        try:
            UserProfile.objects.create(username = username,password=password,email = email,phone=phone)
        except:
            return JsonResponse({'code':304,'error':'用户名已经存在'})

        # 生成token，保存用户登录状态
        token = get_token(username) # type:bytes
        token = token.decode() # type:str

        return JsonResponse({'code':200,'username':username,'data':{'token':token}})


def sms_view(request):
    json_str = request.body
    py_obj = json.loads(json_str)
    phone = py_obj['phone']

    cache_key = f'sms_{phone}' # redis 中短信验证码的键
    code = random.randint(100000,999999) # 生成短信验证码
    # 将验证码存入redis缓存中
    cache.set(cache_key,code,5*60) # 5*60 s

    send_auth_code.delay(phone,code)
    return JsonResponse({'code':200})