"""
sms -- send message server
短信验证码模块
"""
import base64
import datetime
import hashlib
import json

import requests

class YunTongXin():
    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, account_id, auth_token,appId,templateId):
        self.account_id = account_id
        self.auth_token = auth_token
        self.appId = appId
        self.templateId = templateId

    # 生成URL
    def get_url(self, sig):
        return YunTongXin.base_url + f"/2013-12-26/Accounts/{self.account_id}/SMS/TemplateSMS?sig={sig}"

    def get_sig(self, timestamp):
        md5 = hashlib.md5()
        str_sign = self.account_id + self.auth_token + timestamp
        md5.update(str_sign.encode())
        sig = md5.hexdigest().upper()
        return sig

    def get_timestamp(self):  # 时间戳
        str_now = datetime.datetime.now()
        timestamp = str_now.strftime('%Y%m%d%H%M%S')
        return timestamp

    # 请求头
    def get_request_header(self, timestamp):
        s = self.account_id+':'+timestamp
        authorization = base64.b64encode(s.encode()).decode() # type:str
        return {
            "Accept": 'application/json',
            "Content-Type": 'application/json;charset=utf-8',
            'Authorization': authorization
        }

    # 请求体
    def get_request_body(self,phone:str,code,expire):
        data = {
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,expire]
        }
        return data

    # 发送请求
    def do_request(self,url,header,body):
        res = requests.post(url=url,headers=header,data=json.dumps(body))
        return res

    def run(self,phone,code,expire):
        timestamp = self.get_timestamp()
        sig = self.get_sig(timestamp)
        url = self.get_url(sig)
        header = self.get_request_header(timestamp)
        body = self.get_request_body(phone,code,expire)
        print('*******************************')
        print('url:',url)
        print('header:',header)
        print('body:',body)
        print('***********************************')
        res = self.do_request(url,header,body)
        return res

if __name__ == '__main__':
    account_id = '8a216da8827c888b0182a4e667040629'
    auth_token = 'eaa09b43a0964019952b4f367ffd1e28'
    appId = '8a216da8827c888b0182a4e668080630'
    templateId = '1'
    yuntongxin = YunTongXin(account_id,auth_token,appId,templateId)
    res = yuntongxin.run('18834388315','123456',3)
    print(res)