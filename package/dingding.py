from datetime import datetime
import json
import requests
import time
from urllib import parse
import hashlib
import hmac
import base64

class DingDingInstance():
    robot_id = ""
    secret = ""
    def __init__(self, robot_id = 'a3fd61c5fb4ce3ee89baaa4fc5abf5bdbda9e416a935ca4c7a5b5aa35f61d3e2',
                 secret = 'SEC7f877ee56dbc9356d540cb97cbfa8d088b278f2532fe78b9bea36fa907f1f382'):
        self.robot_id = robot_id
        self.secret = secret

    # ===发送钉钉相关函数
    # 计算钉钉时间戳
    def cal_timestamp_sign(self, secret):
        # 根据钉钉开发文档，修改推送消息的安全设置https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        # 也就是根据这个方法，不只是要有robot_id，还要有secret
        # 当前时间戳，单位是毫秒，与请求调用时间误差不能超过1小时
        # python3用int取整
        timestamp = int(round(time.time() * 1000))
        # 密钥，机器人安全设置页面，加签一栏下面显示的SEC开头的字符串
        secret_enc = bytes(secret.encode('utf-8'))
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = bytes(string_to_sign.encode('utf-8'))
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        # 得到最终的签名值
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        return str(timestamp), str(sign)

    # 发送钉钉消息
    def send_dingding_msg(self, content):
        """
        :param content:
        :param robot_id:  你的access_token，即webhook地址中那段access_token。例如如下地址：https://oapi.dingtalk.com/robot/
    n    :param secret: 你的secret，即安全设置加签当中的那个密钥
        :return:
        """

        try:
            if content == "":
                return
            msg = {
                "msgtype": "text",
                "text": {"content": content + '\n' + datetime.now().strftime("%m-%d %H:%M:%S")}}
            headers = {"Content-Type": "application/json;charset=utf-8"}
            # https://oapi.dingtalk.com/robot/send?access_token=XXXXXX&timestamp=XXX&sign=XXX
            timestamp, sign_str = self.cal_timestamp_sign(self.secret)
            url = 'https://oapi.dingtalk.com/robot/send?access_token=' + self.robot_id + \
                  '&timestamp=' + timestamp + '&sign=' + sign_str
            body = json.dumps(msg)
            r = requests.post(url, data=body, headers=headers, timeout=10)
            print(r.text)
            print('成功发送钉钉')
        except Exception as e:
            print("发送钉钉失败:", e)