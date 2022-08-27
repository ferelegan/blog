from django.db import models
import random

def default_sign():
    signs = ['我已经在原地冲你的背影挥累了手',
             '微笑是我最奢侈的表情，这一生我只有把它泛滥成灾',
             '我们两个爱好一样，但性格大有不同',
             '回忆的故事很长可惜你我时间有限',
             '没资格吃的醋最酸，先动心的人最惨',
             '只是后来我们依然孤单，你换了几站，我依然流浪',
             '我去过很多地方，却只遇见过很少的我们',
             '我也怕你会在我看不见的地方陪着别人',
             '若是回忆能够下酒，那我足够醉却一生',
             '想起你的最初炙热的光芒和现在冷冷的回应']
    return random.choice(signs)

def default_info():
    info = [
        'IT精英',
        'Python大佬',
        'Java开发',
        '前端工程师',
        '商业大鳄',
        '商业小成',
    ]
    return random.choice(info)

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField('用户名',max_length=50,primary_key=True)

    nickname = models.CharField('昵称',max_length=50)
    email = models.EmailField('邮箱')
    password = models.CharField('密码',max_length=32)
    info = models.CharField('个人简介',max_length=150,default=default_info)
    sign = models.CharField('个性签名',max_length=50,default=default_sign)
    avatar = models.ImageField('头像',upload_to='avatar',null=True)

    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('修改时间',auto_now=True)
    phone = models.CharField('手机号',max_length=11,default='')
