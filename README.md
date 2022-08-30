# blog
web project
前后端分离项目
### 用户模块
#### 注册并登录
使用的技术：ajax，CORS，容联云-短信验证，缓存，Redis，celery，JWT<br>
将短信验证码存入redis数据库中。<br>
使用CORS进行跨域请求。<br>
异步框架celery，使用celery做短信验证码功能。<br>
使用token来保存用户登录状态
#### 查看博主信息