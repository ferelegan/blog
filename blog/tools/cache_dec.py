# 三层装饰器做缓存
from django.core.cache import cache
from tools.login_dec import get_user_by_request


def topic_cache(expire):
    def _topic_cache(func):
        def wrapper(request,*args,**kwargs):
            # 构造redis键
            ## 判断是否进行权限过滤
            username = get_user_by_request(request) # 获取访问者
            if username == kwargs['author_id']: # public+private
                # request.get_full_path表示 v1/topics/<author_id>[?category='xxx']
                redis_key = f'cache_topics_self_{request.get_full_path()}'
            else:
                redis_key = f'cache_topics_{request.get_full_path()}'

            # 缓存的核心思想
            ## 判断缓存中是否有数据
            print('redis_key: %s'%redis_key)
            res = cache.get(redis_key)
            if res:
                print('---------redis cache in ----------')
                return res
            else:
                res = func(request,*args,**kwargs)
                cache.set(redis_key,res,expire) # 将结果写入缓存
                return res
        return wrapper
    return _topic_cache