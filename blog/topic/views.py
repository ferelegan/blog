import html
import json

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from tools.cache_dec import topic_cache
from tools.login_dec import login_check, get_user_by_request

# Create your views here.
from topic.models import Topic
from user.models import UserProfile


class TopicView(View):
    # 清除缓存
    def clean_topic_cache(self, request):
        # 当发表文章，删除文章，都要清除缓存，保证数据的一致性
        # 构造redis的缓存键，总共六种
        keys_b = ['cache_topics_self', 'cache_topics_']
        keys_m = request.path_info
        keys_p = ['', '?category=tec', '?category=no-tec']
        all_keys = []
        for key_b in keys_b:
            for key_p in keys_p:
                all_keys.append(key_b + keys_m + key_p)
        # 删除所有缓存
        cache.delete_many(all_keys)

    # 博客列表页的返回数据
    def get_topics_res(self, original_topics, user):
        topics = []
        for topic in original_topics:
            data = {}
            data['id'] = topic.id
            data['title'] = topic.title
            data['category'] = topic.category
            data['introduce'] = topic.introduce
            data['created_time'] = topic.created_time
            data['author'] = user.nickname
            topics.append(data)
        res = {'code': 200, 'data': {}}
        res['data']['nickname'] = user.nickname
        res['data']['topics'] = topics
        return res

    # 博客详情页的返回数据
    def get_topic_res(self, user, topic,is_self,t_id):
        # 第一部分，博客详情内容
        res = {'code': 200, 'data': {}}
        res['data']['nickname'] = user.nickname
        res['data']['title'] = topic.title
        res['data']['category'] = topic.category
        res['data']['content'] = topic.content
        res['data']['introduce'] = topic.introduce
        res['data']['created_time'] = topic.created_time
        res['data']['author'] = user.username
        # 第二部分，上、下一篇博客
        ## 是否使用权限过滤
        if is_self: # 博主访问，public+private
            topic_last = Topic.objects.filter(id__lt = t_id,author = user).last()
            topic_next = Topic.objects.filter(id__gt = t_id,author = user).first()
        else:
            topic_last = Topic.objects.filter(id__lt=t_id, author=user,limit='public').last()
            topic_next = Topic.objects.filter(id__gt=t_id, author=user,limit='public').first()
        # 判断是否有上一篇和下一篇
        if topic_last:
            res['data']['last_id'] = topic_last.id
            res['data']['last_title'] = topic_last.title
        else:
            res['data']['last_id'] = None
            res['data']['last_title'] = None
        if topic_next:
            res['data']['next_id'] = topic_next.id
            res['data']['next_title'] = topic_next.title
        else:
            res['data']['next_id'] = None
            res['data']['next_title'] = None
        # 第三部分，评论
        res['data']['message']={}
        res['data']["messages_count"] = 0

        return JsonResponse(res)

    # 博客列表页及博客详情页
    @method_decorator(topic_cache(600))
    def get(self, request, author_id):
        try:
            user = UserProfile.objects.get(username=author_id)
        except:
            return JsonResponse({'code': 404, 'error': '查无此人'})
        # 是否进行权限过滤
        is_self = False
        visitor = get_user_by_request(request)
        if visitor == author_id:
            is_self = True

        t_id = request.GET.get('t_id')
        if t_id:  # 博客详情页
            if is_self:
                try:
                    topic = Topic.objects.get(id=t_id,author = user)
                except:
                    return JsonResponse({'code': 405, 'error': '无此博客'})
            else:
                try:
                    topic = Topic.objects.get(id=2,author = user,limit='public')
                except:
                    return JsonResponse({'code': 405, 'error': '无此博客'})
            res = self.get_topic_res(user, topic,is_self,t_id)
            return res

        else:  # 博客列表页
            # 分类讨论，是否有权限，是否有分类，总共4种情况
            is_category = False
            category = request.GET.get('category', None)
            if category in ['tec', 'no-tec']:
                is_category = True
            if is_self:  # 博主访问，public+private
                if is_category:  # 分类
                    original_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:  # 不分类
                    original_topics = Topic.objects.filter(author_id=author_id)
            else:  # 非博主访问，public
                if is_category:
                    original_topics = Topic.objects.filter(author_id=author_id, category=category, limit='public')
                else:
                    original_topics = Topic.objects.filter(author_id=author_id, limit='public')

            # 组织传输的数据格式,写在此函数内，显得函数太过庞大，故封装成函数
            res = self.get_topics_res(original_topics, user)

            return JsonResponse(res)

    # 发表博客
    @method_decorator(login_check)
    def post(self, request, author_id):
        json_str = request.body
        py_obj = json.loads(json_str)

        title = html.escape(py_obj['title'])  # 做转义，防止xss攻击
        category = py_obj['category']
        limit = py_obj['limit']
        content = py_obj['content']  # 使用富文本编辑器，已经转义
        introduce = py_obj['content_text'][:30]

        # 数据校验
        if not title or not content:
            return JsonResponse({'code': 401, 'error': '文章标题或内容不能为空'})
        if category not in ['tec', 'no-tec']:
            return JsonResponse({'code': 402, 'error': '分类错误'})
        if limit not in ['public', 'private']:
            return JsonResponse({'code': 403, 'error': '权限错误'})

        # 数据入库
        self.clean_topic_cache(request)
        Topic.objects.create(title=title, content=content, introduce=introduce, category=category, limit=limit,
                             author_id=author_id)

        return JsonResponse({'code': 200, 'username': author_id})
