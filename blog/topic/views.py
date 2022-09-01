import html
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from tools.login_dec import login_check, get_user_by_request

# Create your views here.
from topic.models import Topic
from user.models import UserProfile

# 博客列表页
def get_topics_res(original_topics,user):
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
    res = {'code':200,'data':{}}
    res['data']['nickname'] = user.nickname
    res['data']['topics'] = topics
    return res

class TopicView(View):
    def get(self,request,author_id):
        try:
            user = UserProfile.objects.get(username=author_id)
        except:
            return JsonResponse({'code':404,'error':'查无此人'})

        # 分类讨论，是否有权限，是否有分类，总共4种情况
        username = get_user_by_request(request)
        is_category = False
        category = request.GET.get('category',None)
        if category in ['tec','no-tec']:
            is_category = True
        if username == author_id: # 博主访问，public+private
            if is_category: # 分类
                original_topics = Topic.objects.filter(author_id=author_id,category=category)
            else: # 不分类
                original_topics = Topic.objects.filter(author_id=author_id)
        else: # 非博主访问，public
            if is_category:
                original_topics = Topic.objects.filter(author_id=author_id, category=category,limit = 'public')
            else:
                original_topics = Topic.objects.filter(author_id=author_id,limit='public')

        # 组织传输的数据格式,写在此函数内，显得函数太过庞大，故封装成函数
        res = get_topics_res(original_topics,user)

        return JsonResponse(res)

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
        Topic.objects.create(title=title,content=content,introduce=introduce,category=category,limit=limit,author_id=author_id)

        return JsonResponse({'code': 200, 'username': author_id})
