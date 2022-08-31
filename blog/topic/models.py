from django.db import models

# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
    title = models.CharField('文章标题',max_length=50)
    category = models.CharField('文章分类',max_length=20) # ['tec','no-tec']
    limit = models.CharField('文章权限',max_length=10) # ['public','private']
    introduce = models.CharField('文章简介',max_length=90)
    content = models.TextField('文章内容')

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(to=UserProfile,on_delete=models.CASCADE)
