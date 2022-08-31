import html
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from tools.login_dec import login_check


# Create your views here.
from topic.models import Topic


class TopicView(View):
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
        if category not in ['tec', 'no-tec']:
            return JsonResponse({'code': 401, 'error': '分类错误'})
        if limit not in ['public', 'private']:
            return JsonResponse({'code': 402, 'error': '权限错误'})

        # 数据入库
        Topic.objects.create(title=title,content=content,introduce=introduce,category=category,limit=limit,author_id=author_id)

        return JsonResponse({'code': 200, 'username': author_id})
