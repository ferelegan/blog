import jwt
from django.conf import settings
from django.http import JsonResponse
from user.models import UserProfile

# 登录认证装饰器
def login_check(func):
    def warp(request,*args,**kwargs):
        token = request.META.get('HTTP_AUTHORIZATION') # 获取前端提交的请求头中的token
        if not token:
            return JsonResponse({'code':307,'error':'请先登录'})
        try:
            payload = jwt.decode(token,settings.JWT_TOKEN_KEY)
        except:
            return JsonResponse({'code':307,'error':'请先登录'})
        username = payload['username']
        user = UserProfile.objects.get(username = username)
        request.myuser = user

        return func(request,*args,**kwargs)
    return warp

def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    # 校验token
    try:
        payload = jwt.decode(token,settings.JWT_TOKEN_KEY)
    except:
        return None
    # 获取登录用户名
    username = payload['username']
    return username