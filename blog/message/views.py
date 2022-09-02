import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.login_dec import login_check
from topic.models import Topic


@login_check
def message_view(request,t_id):
    json_str = request.body
    py_obj = json.loads(json_str)

    user = request.myuser
    try:
        topic = Topic.objects.get(id=t_id)
    except:
        return JsonResponse({'code':501,'error':'无此博客'})
    message_id = py_obj.get('parent_id',0)

    # 数据入库
    Message.objects.create(content = py_obj['content'],parent_message=message_id,
                           publisher = user,topic=topic)
    return JsonResponse({'code':200})