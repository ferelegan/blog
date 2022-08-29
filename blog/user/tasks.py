from blog.celery import app
from tools.sms import YunTongXin
from django.conf import settings

# 任务函数
@app.task
def send_auth_code(phone,code):
    yuntongxin = YunTongXin(settings.SMS_ACCOUNT_ID, settings.SMS_AUTH_TOKEN, settings.SMS_APP_ID,
                            settings.SMS_TEMPLATE_ID)
    res = yuntongxin.run(phone, str(code), expire=5)  # type:request.models.Response
    res = res.json()
    # if res['statusCode'] != '000000':
    #     return JsonResponse({'code':304,'error':'手机号输入有误'})
    print(res)