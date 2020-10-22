import logging
import threading
import time
import os
import math
import re
import json
import requests, pickle
from requests.exceptions import RequestException
from http.cookiejar import MozillaCookieJar


class PeopleBot(threading.Thread):
  session = requests.session()
  headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "sec-fetch-dest": "empty",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36\
                        (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
    # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://people.bytedance.net",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "referer": "https://people.bytedance.net/hire/referral/position",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
  }


  def __init__(self, logger=None):
    super().__init__()
    if logger is None:
      logger = logging.getLogger()
    self.logger = logger
    self.session.cookies = MozillaCookieJar('.cookiejar')
    if os.path.exists('cookiejar'):
      # Load saved cookies from the file and use them in a request
      self.logger.info('loading saved cookies')
      self.session.cookies.load(ignore_discard=True)

  def login(self):
    '''
    登录
    '''
    url = 'https://people.bytedance.net/hire/referral/position';
    resp = self.session.get(url, headers=self.headers)
    # print(resp.text)
    matches = re.search(r',\\x22name\\x22\:\\x22([^,]+)\\x22,', resp.text)
    
    if not matches:
      self.logger.info('=====login failed====:')
      return
    name = matches.group(1)
    if not name or name == 'null':
      self.logger.error('=====login failed====:')
      return
    self.logger.info('=====login success====:' + name)

    self.session.cookies.save()

  def process_resume(self, file_path, job_id):
    token = self.get_token()
    upload_info = self.upload_file(token, file_path)
    attachment_id = upload_info.get('id')
    resume_url = upload_info.get('url')
    resume_name = upload_info.get('name')

    create_token = self.create_resume(resume_url, resume_name)
    talent = self.get_parse_progress(create_token)
    self.apply_job(job_id, talent, attachment_id)
    return

  def get_token(self):
    url = 'https://people.bytedance.net/atsx/api/talent/get_upload_token/'
    self.logger.info('start get token')

    resp = self.session.get(url)
    msg = resp.json()
    if msg.get('code') == 0:
      token = msg['data']['token']
      self.logger.info('got token: ' + token)
      return token
    else:
      self.logger.error('get token error' + resp.text)
  def upload_file(self, token:str, file_path:str):
    '''
    上传文件
    return: {"id":"6878213317196286221","url":"https://recruitment.kundou.cn/blob/fd6e1e9434f4a592kfp8iuuk5b7c678559ffa239/","name":"filename.pdf","token":"fd6e1e9434f4a592kfp8iuuk5b7c678559ffa239"}
    '''
    if not token or not file_path:
      self.logger.error('invalid token or file error: token= %s, file=%s' % (token, file_path))
    url = 'https://people.bytedance.net/atsx/blob/%s/' % (token)

    with open(file_path, 'rb') as file:
      if not file:
        self.logger.error('invalid file error')
        return None
      self.logger.info('upload file:' + file_path)
      resp = self.session.post(url, headers=self.headers, files={
        'content': (file_path.split('/')[-1], file)
      })

      msg = resp.json()
      if msg.get('code') != 0:
        self.logger.error('upload error')
        return None
      data = msg.get('data')
      self.logger.info('upload success: ' + resp.text)
      return data

  def create_resume(self, resume_url, file_name):
    '''
    创建简历
    return: token
    '''
    url = 'https://people.bytedance.net/atsx/api/talent/resume/parse/create/'
    self.logger.info('start create resume: url=%s, filename=%s' %(resume_url, file_name))
    resp = self.session.post(url, headers=self.headers, data={
      'resume_url': resume_url,
      'file_name': file_name
    })
    msg = resp.json()
    if msg.get('code') != 0:
      self.logger.error('create resume error: ' + resp.text)
      return None

    self.logger.info('create resume success: ' + resp.text)
    token = msg['data']['token']
    return token

  def get_parse_progress(self, token: str):
    '''
    解析简历结果，可能返回解析中的结果
    return: talent
    {"code":0,"success":true,"data":{"parse_result":1,"progress":51,"talent":null,"BaseResp":{"StatusMessage":"SUCCESS","StatusCode":0,"Extra":null}},"message":"OK"}
    {
      "code": 0,
      "success": true,
      "data": {
        "parse_result": 2,
        "progress": 99,
        "talent": {
          "name": "陈多美",
          "mobile": "18811111111",
          "email": "xxxx@sss.com",
          "experience_years": 1,
          "gender": null,
          "mobile_code": "CN_1",
          "age": 26,
          "hometown_location": null,
          "current_location": null,
          "willing_location_list": null,
          "self_evaluation": "有很强的学习能力,对于新环境能很快适应并投入到新环境中,具有较强的学习能力、工作适应能力和信息搜集能力,善于接受新事物,团队意识及适应能力强,抗压能力好,喜欢面对挑战迎难而上。",
          "education_list": [
            {
              "degree": 6,
              "school": "xxxx学校",
              "field_of_study": "电子信息工程",
              "start_time": "2018-08-01",
              "end_time": "2020-03-01"
            }
          ],
          "career_list": [
            {
              "company": "北京优炫软件股份有限公司",
              "title": "",
              "desc": "工作内容: 负责云计算平台的镜像,存储,权限,以及计算模块的设计和开发,负责 UxDisk 的设计开发以及上线。",
              "start_time": "2018-08-01",
              "end_time": "2020-03-01"
            }
          ]
        }
      }
    }
    '''
    url = 'https://people.bytedance.net/atsx/api/talent/resume/parse/progress/'
    params = { 'token': token }
    talent = None
    max_times = 10
    times = 0
    while not talent or times >= max_times:
      resp = self.session.get(url, params=params)
      msg = resp.json()
      if msg.get('code') != 0 or not msg['data']:
        self.logger.error('parse resume failed! ' + token)
        return None
      data = msg['data']
      self.logger.info('parse resume progress: ' + resp.text)
      talent = data.get('talent')
      times = times + 1
      time.sleep(2)
    if not talent:
      self.logger.error('parse resume timeout ' + token)
      return None
    self.logger.info('parse resume success: ' + talent.get('name') )
    return talent

  def apply_job(self, job_id:str, talent:dict, attachment_id: str):
    url = 'https://people.bytedance.net/atsx/api/referral/applications/'
    resume = self._fix_talent_resume(talent, attachment_id)
    if not resume:
      self.logger.error('format resume none error')
      return
    data = {
      'job_post': {
        'job_post_id': job_id
      },
      'referral_method': 1,
      "extra_info": {
        "relationship": 0,
        "familiarity": 0
      },
      "resume": resume
    }
    headers = self.headers.copy()
    headers['Content-Type'] = 'application/json'
    resp = self.session.post(url, data=json.dumps(data, ensure_ascii=True), headers=headers)
    print(resp.request.body)
    print('apply result:', resp.text)


  def _fix_talent_resume(self, talent:dict, attachment_id:str):
    '''
    修复解析到的简历信息，必备信息不完备，简单修复
    '''

    key_map = {
      'mobile_country_code': 'mobile_code',
      'mobile_number': 'mobile',
    }
    result = {}
    keys = ['name', 'mobile_country_code', 'mobile_number', 'email', 'education_list', 'career_list', 'experience_years']
    print(talent)
    for key in keys:
      print('============', result)
      if key in key_map:
        old_key = key_map[key]
        result[key] = talent[old_key]
      else:
        result[key] = talent[key]

    default_today = time.strftime("%Y-%m-%d", time.localtime(time.time())) 

    # print(result['education_list'][0].get('start_time') )
    # test = result['education_list'][0].get('start_time')
    # test_time = time.strptime(test, "%Y-%m-%d") * 1000
    # print(test_time)

    result['education_list'] = list(map(lambda edu:  {
      "degree": edu.get('degree', ''),
      "school": edu.get('school', ''),
      "major": edu.get('field_of_study', ''),
      "start_time": self.convert_time(edu.get('start_time')),
      "end_time": self.convert_time(edu.get('end_time'))
    }, result['education_list']))

    result['career_list'] = list(map(lambda career:  {
      "company": career.get('company', ''),
      "title": career.get('title', '工程师'),
      "description": career.get('desc', ''),
      "start_time": self.convert_time(career.get('start_time')),
      "end_time": self.convert_time(career.get('end_time'))
    }, result['career_list']))

    result['attachment_id'] = attachment_id

    if not result.get('name') or not result.get('mobile_number'):
      self.logger.error('fix resume info failed for key info missing:' + json.dumps(result, ensure_ascii=False))
      return None

    if not result.get('mail'):
      result['mail'] = 'xxx@xxx.com'

    return result

  def convert_time(self, date:str):
    if not date or not re.search(r'\d+\-\d+\-\d+',date):
      return int(time.time() * 1000)
    result = math.floor(time.mktime(time.strptime(date, "%Y-%m-%d")) * 1000)
    return result;
