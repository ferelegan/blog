import html
import json

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from message.models import Message
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
        res['data']['messages']=[]
        messages = Message.objects.filter(topic_id = t_id)
        reply_dict = {} # 存放回复
        messages_count = 0 # 评论的数量
        for message in messages:
            if message.parent_message == 0: # 评论
                m_dict = {}
                m_dict['id'] = message.id
                m_dict['content'] = message.content
                m_dict['publisher'] = message.publisher.nickname
                m_dict['publisher_avatar'] = str(message.publisher.avatar)
                m_dict['reply'] = []
                m_dict['created_time'] = message.created_time.strftime('%Y-%m-%d %H:%M:%S')
                res['data']['messages'].append(m_dict)
                messages_count += 1
            else: # 回复
                reply = {} # 存放每一条回复
                reply_dict.setdefault(message.parent_message,[])
                reply['msg_id'] = message.id
                reply['content'] = message.content
                reply['created_time'] = message.created_time.strftime('%Y-%m-%d %H:%M:%S')
                reply['publisher'] = message.publisher.nickname
                reply['publisher_avatar'] = str(message.publisher.avatar)
                reply_dict[message.parent_message].append(reply)
        # 进行组合
        for parent_message in res['data']['messages']:
            if parent_message['id'] in reply_dict:
                parent_message['reply'] = reply_dict[parent_message['id']]

        res['data']["messages_count"] = messages_count

        return JsonResponse(res)

        # result = {'code': 200, 'data': {}}
        # result['data']['nickname'] = author.nickname
        # result['data']['title'] = author_topic.title
        # result['data']['category'] = author_topic.category
        # result['data']['content'] = author_topic.content
        # result['data']['introduce'] = author_topic.introduce
        # result['data']['author'] = author.nickname
        # result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        #
        # # 第二部分
        #
        # if is_self:  # 是博主访问自己的博客
        #     # 获取上一篇文章的对象
        #     last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author.username).last()
        #     # 获取下一篇文章对象
        #     next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        # else:
        #     last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author.username,
        #                                       limit='public').last()
        #     next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
        # if last_topic:
        #     result['data']['last_id'] = last_topic.id
        #     result['data']['last_title'] = last_topic.title
        # else:
        #     result['data']['last_id'] = None
        #     result['data']['last_title'] = None
        # if next_topic:
        #     result['data']['next_id'] = next_topic.id
        #     result['data']['next_title'] = next_topic.title
        # else:
        #     result['data']['next_id'] = None
        #     result['data']['next_title'] = None
        #
        # # 第三部分
        # all_ms = Message.objects.filter(topic=author_topic).order_by('-created_time')  # 源数据
        # msg_list = []  # 目标数据
        # r_dict = {}  # 目标数据的后半部分
        # msg_count = 0  # 只统计评论数量，不统计回复数量
        # for msg in all_ms:
        #     if msg.parent_message:  # 回复
        #         r_dict.setdefault(msg.parent_message, [])
        #         r_dict[msg.parent_message].append({
        #             "publisher": msg.publisher.nickname,
        #             'publisher_avatar': str(msg.publisher.avatar),
        #             'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        #             'content': msg.content,
        #             'msg_id': msg.id,
        #         })
        #     else:  # 评论
        #         # publisher = UserProfile.objects.get()
        #         msg_list.append({
        #             'id': msg.id,
        #             'content': msg.content,
        #             'publisher': msg.publisher.nickname,
        #             'publisher_avatar': str(msg.publisher.avatar),
        #             'reply': [],
        #             'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        #         })
        #         msg_count += 1
        # # 评论和回复进行关联
        # for m in msg_list:
        #     if m['id'] in r_dict:
        #         m['reply'] = r_dict[m['id']]
        # result['data']['messages'] = msg_list
        # result['data']['messages_count'] = msg_count
        #
        # return JsonResponse(result)

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
                    topic = Topic.objects.get(id=t_id,author = user,limit='public')
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

