# -*- coding: utf-8 -*-
import logging
import threading
import time
import random
import os
import re
import json
import requests
import uuid
from requests.exceptions import RequestException
import qrcode
import paho.mqtt.client as mqtt
from bossbot import protobuf_json
from bossbot.proto_pb2 import TechwolfChatProtocol


class BossBot(threading.Thread):
    uid = None
    user_id = None
    token = None

    client_id = None

    bosses = {}
    resumes = []

    geeks = {}
    geek_feeds = {}

    job_ids = []
    hostname = 'ws.zhipin.com'
    port = 443
    clientId = '19833398'
    timeout = 60
    keepAlive = 100
    topic = '/chatws'
    client = None
    session = requests.session()

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "sec-fetch-dest": "empty",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36\
                            (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://login.zhipin.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "referer": "https://login.zhipin.com/?ka=header-login",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    def __init__(self, logger=None):
        super().__init__()
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

    def _gen_qrcode(self):
        """
        生成二维码
        :return:
        """
        url = "https://login.zhipin.com/wapi/zppassport/captcha/randkey"
        resp = requests.get(url, headers=self.headers, verify=False)
        qr_id = resp.json()['zpData']['qrId']
        # 实例化QRCode生成qr对象
        qr_code = qrcode.QRCode()
        # 传入数据
        qr_code.add_data(qr_id)
        qr_code.make(fit=True)
        # 生成二维码
        img = qr_code.make_image()
        # 展示二维码
        img.show()
        return qr_id

    def _scan(self, qr_id):
        """
        扫码及获取登陆信息
        :param qr_id: 二维码的qr_id
        :return:
        """

        url = "https://login.zhipin.com/scan?uuid=%s&_%s" % (qr_id, str(int(time.time() * 1000)))
        self.session.get(url, headers=self.headers)

        url = "https://login.zhipin.com/wapi/zppassport/qrcode/scanLogin?qrId=%s&_=%s" % (
            qr_id, str(int(time.time() * 1000)))
        self.session.get(url, headers=self.headers)

        url = "https://login.zhipin.com/wapi/zppassport/qrcode/dispatcher?qrId=%s&_=%s" % (
            qr_id, str(int(time.time() * 1000)))
        self.session.get(url, headers=self.headers)

        url = "https://www.zhipin.com/chat/im"
        resp = self.session.get(url, headers=self.headers)
        zp_data =  resp.text
        print('zp data %s' % (zp_data))
        self.uid = re.search(r'uid:(\d*)', zp_data).group(1)
        self.user_id = requests.utils.dict_from_cookiejar(self.session.cookies)['t']
        self.token = re.search(r'token: ?"(.*)"', zp_data).group(1)

    def _jobs(self):
        url = "https://www.zhipin.com/chat/im"
        resp = self.session.get(url, headers=self.headers)
        zp_data =  resp.text
        self.job_ids = re.findall(r'data-jobid="([a-zA-Z0-9_\-=~]{28})"', zp_data)
        print("职位：", self.job_ids)
    def release_data(self):
        try:
            self.geek_feeds = {}
            self.geeks = {}
        except:
            pass

    def login(self, uid=None, user_id=None, token=None, client_id=None):
        """
        登陆账号
        使用扫码登陆后，会打印下面的3个参数值，长期有效。之后可以直接它们登陆，跳过扫码步骤
        :param uid: 登陆后返回的uid
        :param user_id: 登陆后返回的user_id
        :param token: 登陆后返回的token
        :return:
        """
        if not client_id:
            client_id = self.get_client_id(16)

        self.client_id = client_id

        if uid is None or user_id is None or token is None:
            qr_id = self._gen_qrcode()
            self._scan(qr_id)
        else:
            self.uid = uid
            self.user_id = user_id
            self.token = token
            requests.utils.add_dict_to_cookiejar(self.session.cookies,
                                                 {"t": user_id, "wt": user_id})

        print('已登陆: uid: %s, user_id: %s, token: %s' % (self.uid, self.user_id, self.token))

        self._jobs()
        #self.get_boss_list()
        #self.get_resumes()

    def _on_connect(self, client, userdata, flags, rc):
        """
        即时通讯 websocket 连接成功
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        self.logger.info("Connected with result code %s", str(rc))
        # client.subscribe(self.topic)
        self.on_connect(client, userdata, flags, rc)

    def on_connect(self, client, userdata, flags, rc):
        """
        即时通讯 websocket 连接成功
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        pass


    def _on_disconnect(self, client, userdata, rc):
        """
        即时通讯 websocket 断开连接
        :param client:
        :param userdata:
        :param rc:
        :return:
        """
        if rc != 0:
            self.logger.info("Unexpected disconnection.")

    def _on_message(self, client, userdata, msg):
        """
        收到消息
        :param client:
        :param userdata:
        :param msg: 收到的消息内容
        :return:
        """
        try:
            print('on-message:', msg)
            protocol = TechwolfChatProtocol()
            protocol.ParseFromString(msg.payload)
            data = protobuf_json.pb2json(protocol)
            self.logger.debug('receive: %s', json.dumps(data, ensure_ascii=False))
            print('receive: %s', json.dumps(data, ensure_ascii=False))
            if data['type'] == 1:
                #message = data['messages'][-1]
                for message in data['messages']:
                    body = message['body']
                    if body['type'] == 1:
                        # 文字消息

                        self.on_text_message(data, message['from']['uid'], body['text'], message.get('securityId', None))
                    elif body['type'] == 7 and message['from']['uid'] != int(self.uid):
                        # 求简历
                        self.on_request_send_geek_resume(data, message['from']['uid'], message['mid'])
                    elif body['type'] == 12 and message['from']['uid'] != int(self.uid):
                        # 获得简历
                        self.on_get_geek_resume(data, message['from']['uid'], message['mid'], message['from']['name'])
                    elif body['type'] == 9:
                        self.on_geek_greeting(data, message['from']['uid'], message['mid'], message.get('securityId', None))
            elif data['type'] == 3:
                for message in data['messages']:
                    body = message['body']
                    #发简历
                    if body['type'] == 7 and message['from']['uid'] != int(self.uid):
                        self.on_request_send_geek_resume(data, message['from']['uid'], message['mid'])
            elif data['type'] == 4:
                # /message/suggest
                pass
            elif data['type'] == 6:
                # 同步已读未读
                pass

        except Exception as err:
            print('==============on message error==========', err)

    def on_geek_greeting(self, data, uid, mid, securityId):
        print('招呼:%s', data)

    def on_text_message(self, data, boss_id, msg, securityId):
        """
        文本 消息回调函数。
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param msg: 文本内容
        :return:
        """
        self.logger.info('收到文字消息:%s', msg)

    def on_request_resume_message(self, data, boss_id, mid):
        """
        请求发送简历 消息回调函数
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param mid: 消息id，如果需要同意或者拒绝，需要此id
        :return:
        """
        self.logger.info('收到boss:%s,请求发送一份简历', boss_id)
        self.accept_resume(boss_id, mid, self.resumes[0]['resumeId'])
    def on_get_geek_resume(self, data, geek_id, mid, name):
        self.logger.info('收到简历: %s', name)

    def on_request_send_geek_resume(self, data, geek_id, mid):
        """
        geek请求发送简历 消息回调函数
        """
        self.logger.info('收到geek:%s,请求发送一份简历', geek_id)
        self.accept_geek_resume(geek_id, mid)

    def send_message(self, boss_id: str, msg: str):
        """
        发送文本消息
        :param boss_id: 对方boss_id
        :param msg: 消息内容
        :return:
        """
        mid = int(time.time() * 1000)
        chat = {
            "type": 1,
            "messages": [
                {
                    "from": {
                        "uid": "0"
                    },
                    "to": {
                        "uid": "0",
                        "name": self.bosses[boss_id]['encryptBossId']
                    },
                    "type": 1,
                    "mid": mid,
                    "time": int(time.time() * 1000),
                    "body": {
                        "type": 1,
                        "templateId": 1,
                        "text": msg
                    },
                    "cmid": mid
                }
            ]
        }
        chat_protocol = protobuf_json.json2pb(TechwolfChatProtocol(), chat)
        self.client.publish(self.topic, payload=chat_protocol.SerializeToString(), qos=0)
    def get_client_id(self, num = 16):
        uln = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        rs = random.sample(uln, num)
        return ''.join(rs)
    def run(self):
        # "ws-CD090DC8307DE0MM" 中的后半段
        if not self.client_id:
            self.client_id = self.get_client_id(16)
        self.client = mqtt.Client(client_id='ws-%s' % (self.client_id), clean_session=True,
                                  transport="websockets")
        self.client.username_pw_set(self.token, self.user_id)
        headers = {
            "Cookie": "t=%s; wt=%s;" % (self.user_id, self.user_id)
        }
        self.client.ws_set_options(path=self.topic, headers=headers)
        self.client.tls_set()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.enable_logger(self.logger)

        ##30秒ping一次。60秒的话会断开连接
        self.client.connect(self.hostname, self.port, 30)
        self.client.loop_forever()

    def get_boss_list(self):
        """
        获取沟通过的boss信息
        :return:
        """
        for page in range(1, 10):
            url = "https://www.zhipin.com/wapi/zprelation/friend/getGeekFriendList.json?page=" \
                  + str(page)
            resp = self.session.get(url, headers=self.headers)
            new_friends = resp.json()['zpData'].get('result', [])
            for friend in new_friends:
                self.bosses[str(friend['uid'])] = friend

    def get_boss_data(self, boss_id, source_type="0"):
        """
        获取某个boss的详细信息（包含当前沟通的职位信息等）
        :param boss_id:
        :param source_type: 未知
        :return: boss的相信信息
        """
        if self.bosses[boss_id].get('bossData', None):
            return self.bosses[boss_id]['bossData']

        url = "https://www.zhipin.com/wapi/zpgeek/chat/bossdata.json"
        params = {
            "bossId": self.bosses[boss_id]['encryptBossId'],
            "bossSource": source_type,
            "securityId": self.bosses[boss_id]['securityId']
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.bosses[boss_id]['bossData'] = resp.json()['zpData']
        return self.bosses[boss_id]['bossData']

    def get_history_msg(self, boss_id):
        """
        获取与某个boss的历史聊天数据
        :param boss_id: boss_id
        :return: 聊天数据
        """
        if self.bosses[boss_id].get('messages', None):
            return self.bosses[boss_id]['messages']

        url = "https://www.zhipin.com/wapi/zpchat/geek/historyMsg"
        params = {
            "bossId": self.bosses[boss_id]['encryptBossId'],
            "groupId": self.bosses[boss_id]['encryptBossId'],
            "maxMsgId": "0",
            "c": "20",
            "page": "1",
            "src": "0",
            "securityId": self.bosses[boss_id]['securityId'],
            "loading": "true",
            "_t": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.bosses[boss_id]['messages'] = resp.json()['zpData'].get('messages', [])
        return self.bosses[boss_id]['messages']

    def request_send_resume(self, boss_id, resum_id):
        """
        请求发送简历
        :param boss_id: boss_id
        :param resum_id: 简历id
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/geek/new/requestSendResume.json"
        params = {
            "bossId": boss_id,
            "resumeId": resum_id,
            "toSource": "0"
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()

    def accept_resume(self, boss_id, mid, resume_id):
        """
        同意发送简历
        :param boss_id: boss_id
        :param mid: boss发送的请求简历消息的mid
        :param resume_id: 要发送的简历id
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/geek/new/acceptResume.json"
        params = {
            "bossId": boss_id,
            "mid": mid,
            "toSource": "0",
            "resumeId": resume_id
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()

    def get_resumes(self):
        """
        获取我的简历列表
        :return: 简历列表
        """
        url = "https://www.zhipin.com/wapi/zpgeek/resume/attachment/checkbox.json"
        params = {
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.resumes = resp.json()['zpData'].get('resumeList', [])
        return self.resumes

    def get_geeks(self, job_id, page = 1):
        """
        获取推荐牛人列表
        :return: 牛人列表
        """
        url = "https://www.zhipin.com/wapi/zpboss/h5/boss/recommendGeekList"
        params = {
            "jobid": job_id,
            "status": 0,
            "refresh": int(time.time() * 1000),
            "source": 1,
            "age": "16,-1",
            "gender": "-1",
            "switchJobFrequency": "-1",
            "exchangeResumeWithColleague": "0",
            "recentNotView": "-1",
            "activation": "-1",
            "school": "-1",
            "major": "0",
            "experience": 0,
            "degree": 0,
            "salary": 0,
            "intention": -1,
            "jobId": job_id,
            "page": page,
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        r = resp.json()
        
        geeks = r['zpData'].get('geekList', [])
        if len(geeks) == 0:
            print('got none geeks, ', r)
        for geek in geeks:
            self.geeks[str(geek['encryptGeekId'])] = geek
        return geeks
        
    def get_geek_feeds(self, page = 1, MAX = 100):
        """
        获取推荐牛人列表
        :return: 牛人列表
        """
        url = "https://www.zhipin.com/wapi/zprelation/friend/getBossFriendList.json"
        params = {
            "page": page,
            "slm": 0,
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        new_friends = resp.json()['zpData'][0:MAX]
        for friend in new_friends:
            self.geek_feeds[str(friend['uid'])] = friend
        return new_friends
    def get_geek_securityId(self, geek_id):
        geek_id = str(geek_id)
        if not (geek_id in self.geek_feeds):
            self.get_geek_feeds()

        # if geek_id in self.geeks:
        #     return self.geeks[geek_id]['geekCard']['securityId']
        if geek_id in self.geek_feeds:
            return self.geek_feeds[geek_id]['securityId']
        
        return ''
    def get_geek_data(self, geek_id, securityId = ''):
        """
        获取牛人信息
        :return: 牛人信息
        """
        if not securityId:
            securityId = self.get_geek_securityId(geek_id)
        geek_id = str(geek_id)
        url = "https://www.zhipin.com/wapi/zpboss/h5/chat/geek.json"
        params = {
            "uid": geek_id,
            "geekSource": 0,
            "securityId": securityId,
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        data = resp.json()['zpData']['data']
        print('=====geek datas detail', data)
        return data

    def process_msg_info(self, msg):
        config = {
            # 我发的文本
            "is_my_text_msg": [
                { "type": 1, "body_type": 1, "self_target": "from" }
            ],
            # 我发过请求简历
            "is_my_request_resume_msg": [
                { "type": 3, "body_type": 7, "self_target": "from" },
                { "type": 1, "body_type": 4, "self_target": "from" },
            ],
            # 已经拿到的简历
            "is_resume": [
                { "type": 1, "body_type": 12, "self_target": "to" },
                { "type": 3, "body_type": 12, "self_target": "to" }
            ],
            # 对方发过简历申请
            "is_geek_resume_request": [
                { "type": 3, "body_type": 7, "self_target": "to" },
                { "type": 1, "body_type": 7, "self_target": "to" }
            ],
        }
        result = {}
        for key in config:
            for conf in config[key]:
                if not result.get(key):
                    result[key] = (msg['type'] == conf['type'] and msg['body']['type'] == conf['body_type'] and str(msg[conf['self_target']]['uid']) == str(self.uid))
        return result

    def brief_msgs_info(self, messages = []):
        result = {}
        for msg in messages:
            res = self.process_msg_info(msg)
            for key in res:
                result[key] = res[key] or bool(result.get(key))
        return result

    def get_geek_msgs(self, geek_id):
        """
        获取与牛人的消息列表
        :return: 消息列表
        """
        url = "https://www.zhipin.com/wapi/zpchat/boss/historyMsg"
        params = {
            "uid": geek_id,
            "geekSource": 0,
            "securityId": self.get_geek_securityId(geek_id),
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()['zpData']['messages']

    def accept_geek_resume(self, geek_id, mid = int(time.time() * 1000)):

        """
        同意牛人发送简历
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/chat/acceptResume.json"
        print(geek_id, mid)
        params = {
            "to": geek_id,
            "mid": mid,
            "aid": 41,
            "action": 0,
            "extend": '',
            "_": str(int(time.time() * 1000))
        }
        print(params)
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()
    def request_geek_resume(self, geek_id):
        """
        同意牛人发送简历
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/wapi/zpchat/exchange/request"
        params = {
            "type": 4,
            "securityId": self.get_geek_securityId(geek_id),
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()


    def greeting_geek(self, encrypt_geek_id):
        """
        打招呼
        """
        url = "https://www.zhipin.com/wapi/zpboss/h5/chat/start"
        card = self.geeks[encrypt_geek_id]['geekCard']
        print(card)
        params = {
            "gid": encrypt_geek_id,
            "suid": '',
            "jid": card['jobId'],
            "expectId": card['expectId'],
            "lid": card['lid'],
            'from': '',
            "securityId": card['securityId'],
            "_": str(int(time.time() * 1000))
        }
        resp = self.session.post(url=url, params=params, headers=self.headers)
        ret = resp.json()
        print("跟牛人打招呼", ret)
        limit = ret.get('zpData', {}).get('limitTitle', '')
        print(limit)
        if limit == '今日沟通已达上限':
            return False
        return True
    def on_download_geek_resume(self, uid, filename, geekData):
        '''
        下载完了一个简历
        '''

    def download_geek_resume(self, uid: str, path: str = os.path.relpath(__file__ + '/../../resumes')):
        """
        必须在打过招呼互相同意之后可以下载
        """
        uid = str(uid)
        geek = self.geek_feeds.get(uid)
        if not geek:
            print('[download] get feeds')
            feeds = self.get_geek_feeds()
            print('[download] get new feeds:', feeds)
        geek = self.geek_feeds.get(uid)
 
        if not geek:
            print('[download] not found geek ', uid)
            return;
        print('download geek:', geek)
        encrypt_uid = geek.get('encryptUid')
        # https://docdownload.zhipin.com/wapi/zpgeek/resume/attachment/download4boss/${encryptUid}
        url = "https://docdownload.zhipin.com/wapi/zpgeek/resume/attachment/download4boss/%s?d=%s" % (encrypt_uid, str(int(time.time() * 1000)))
        print('download url:', url)
        try:
            with self.session.get(url, params={}, headers=self.headers) as r:

                fname = ''
                # print('download headers:', r.headers)
                if "Content-Disposition" in r.headers.keys():
                    fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
                    fname = fname.encode('iso-8859-1').decode('utf-8')[1:-1]
                    # print('download dcode:', fname)
                else:
                    fname = url.split("/")[-1]
                try:
                    geekData = self.get_geek_data(uid)
                    if geekData:
                        fname = geekData.get('position', 'unknown').replace('/', '_') + '|||' + fname
                except:
                    fname = 'unknown' + '|||' + fname
                localtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
                finnalpath = os.path.join(path, localtime)
                if not os.path.exists(finnalpath):
                    os.mkdir(finnalpath)
                save_filename = os.path.join(finnalpath, fname)
                
                if os.path.exists(save_filename):
                    print('[download] file exists', save_filename)
                    return save_filename
                print('[download]:', fname,  '[save]:', save_filename)
                with open(save_filename, 'wb') as file:
                    file.write(r.content)
                self.on_download_geek_resume(uid, save_filename, geekData)
                return save_filename
        except RequestException as e:
            print(e)
            return None
    
    def send_message_geek(self, geek_id: str, msg: str):
        """
        发送文本消息
        :param geek_id: geek_id
        :param msg: 消息内容
        :return:
        """
        print("已经发送: ", msg)
        mid = int(time.time() * 1000)
        chat = {
            "type": 1,
            "messages": [
                {
                    "from": {
                        "uid": "0"
                    },
                    "to": {
                        "uid": "0",
                        "name": self.geek_feeds[geek_id]['encryptUid']
                    },
                    "type": 1,
                    "mid": mid,
                    "time": int(time.time() * 1000),
                    "body": {
                        "type": 1,
                        "templateId": 1,
                        "text": msg
                    },
                    "cmid": mid
                }
            ]
        }
        chat_protocol = protobuf_json.json2pb(TechwolfChatProtocol(), chat)
        self.client.publish(self.topic, payload=chat_protocol.SerializeToString(), qos=0)

    def read_messages(self, message_ids = []):
        """
        发送文本消息
        :param geek_id: geek_id
        :param msg: 消息内容
        :return:
        """
        print("发送已读: ", message_ids)
        if len(message_ids) == 0:
            return
        readTime = int(time.time() * 1000)
        chat = {
            "type": 6,
            "messageRead": list(map(lambda mid: { "userId": self.uid, "messageId": mid, "readTime": readTime }, message_ids))
        }
        print('[read]', chat)
        chat_protocol = protobuf_json.json2pb(TechwolfChatProtocol(), chat)
        self.client.publish(self.topic, payload=chat_protocol.SerializeToString(), qos=0)