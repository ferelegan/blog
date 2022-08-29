import json
import random

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

# Create your views here.
from tools.sms import YunTongXin
from user.models import UserProfile
from django.core.cache import cache

class UserView(View):
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

        return JsonResponse({'code':200})


def sms_view(request):
    json_str = request.body
    py_obj = json.loads(json_str)
    phone = py_obj['phone']

    cache_key = f'sms_{phone}' # redis 中短信验证码的键
    code = random.randint(100000,999999) # 生成短信验证码
    # 将验证码存入redis缓存中
    cache.set(cache_key,code,5*60) # 5*60 s

    yuntongxin = YunTongXin(settings.SMS_ACCOUNT_ID, settings.SMS_AUTH_TOKEN, settings.SMS_APP_ID,
                            settings.SMS_TEMPLATE_ID)
    res = yuntongxin.run(phone,str(code),expire=5)
    res = res.json()
    if res['statusCode'] != '000000':
        return JsonResponse({'code':304,'error':'手机号输入有误'})
    return JsonResponse({'code':200})