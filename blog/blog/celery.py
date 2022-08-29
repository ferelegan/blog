import os
from celery import Celery
from django.conf import settings

# 配置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')

# 创建celery对象
app = Celery('blog')
# 配置celery
app.conf.update(
    # 消息中间件 -- 消息队列
    BROKER_URL = 'redis://:@127.0.0.1:6379/1'
)

# 自动加载任务
app.autodiscover_tasks(settings.INSTALLED_APPS)