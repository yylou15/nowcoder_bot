# -*- coding: utf-8 -*-
import json
import logging
import time
import datetime
import threading
import random
import math
import os
from bossbot import BossBot
from peoplebot import PeopleBot
from examples import filters
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()

# 来自于people, [社招， 实习]
jobs = {
  'HR': ['6843364252502837512', '6843364252502837512'],
  '服务端': ['6860361408367315214', '6704443756197710094'],
  'Android': ['6704530394017958148', '6704433460473235726'],
  '前端': ['6704579151308785928', '6704552316768356615'],
  'iOS': ['6704579151484946692', '6704579127824877831'],
  'Rust': ['6704534498622572807', '6704463170729150724'],
  'C工程师': ['6704534498622572807', '6704463170729150724'],
  '数据': ['6721890202450659592', '6750951560294959374'],
  'AI': ['6717472122249152782', '6753920635681900814'],
  '测试': ['6860742208796018958', '6870404247897950477']
}

# 来自于boss，做了修改
positions = {
	"前端": ["前端开发", "web前端", "JavaScript", "Flash开发", "HTML5", "移动web前端", "Flash开发", "JavaScript", "U3D", "COCOS2DX", "Node.js"],
	"服务端": ["全栈工程师", "GIS工程师", "后端开发", "Java", "C++", "PHP", "C", "C#", ".NET", "Hadoop", "Python", "Delphi", "VB", "Perl", "Ruby", "Golang", "Erlang", "语音/视频/图形开发", "数据采集", "架构师"],
	"iOS": ["iOS"],
    "Android": ["Android"],
	"数据": ["数据", "ETL工程师", "数据仓库", "数据开发", "数据挖掘", "数据分析师", "数据架构师"],
    "AI": ["智能驾驶系统工程师", "反欺诈/风控算法", "人工智能", "数据挖掘", "搜索算法", "自然语言处理", "推荐算法", "算法工程师", "机器学习", "深度学习", "语音识别", "图像识别", "算法研究员"],
	"Rust": ["硬件工程师", "嵌入式", "自动化", "单片机", "电路设计", "驱动开发", "系统集成", "FPGA开发", "DSP开发", "ARM开发", "PCB工艺", "射频工程师"],
    "HR": ["人力资源", "HRBP", "HR", "hrbp", "人力资源总监", "人力资源经理", "HRD", "OD"],

	"项目管理": ["硬件项目经理", "项目经理", "项目主管", "项目助理", "项目专员", "实施顾问", "实施工程师", "需求分析工程师"],
	"通信": ["通信技术工程师", "通信研发工程师", "数据通信工程师", "移动通信工程师", "电信网络工程师", "电信交换工程师", "有线传输工程师", "无线/射频通信工程师", "通信电源工程师", "通信标准化工程师", "通信项目专员", "通信项目经理", "核心网工程师", "通信测试工程师", "通信设备工程师", "光通信工程师", "光传输工程师", "光网络工程师"],
	"高端技术职位": ["高端技术职位", "技术经理", "技术总监", "测试经理", "架构师", "CTO", "运维总监", "技术合伙人"],
    "测试": ["渗透测试", "测试工程师", "自动化测试", "功能测试", "性能测试", "测试开发", "移动端测试", "游戏测试", "硬件测试", "软件测试"],
	"运维/技术支持": ["运维工程师", "运维开发工程师", "网络工程师", "系统工程师", "IT技术支持", "系统管理员", "网络安全", "系统安全", "DBA"],
}

beta_positions = ["项目管理", "通信"]
beta_degrees = ["大专", "专科"]

positionMap = {}
for job_name in positions:
    for pos in positions.get(job_name, []):
        if not positionMap.get(pos):
            positionMap[pos] = job_name

def map_job(filename):
    name = filename.split('/')[-1]
    pos_arr = name.split('|||')
    default_jobs = []
    job_idx = 0
    if '21年应届生' in name or '实习' in name:
        job_idx = -1
    for job_name in jobs:
        if job_name in name:
            default_jobs = jobs[job_name]
            break
    finnal_jobs = default_jobs
    first_jobs = None
    if len(pos_arr) > 1:
        all_pos = pos_arr[0].split('_')
        for pos in all_pos:
            first_job_name = positionMap.get(pos, '')
            first_jobs = jobs.get(first_job_name, None)
            if first_jobs:
                break;

    if first_jobs and len(first_jobs) > 0:
        finnal_jobs = first_jobs

    return finnal_jobs[job_idx]

def geeks_filter(geek):
    '''
    筛选geeks
    geek = {
        expectPositionName: "项目经理",
        edus: [
            {
                degree: "本科",
                school: "北京化工",
                major: "计算机科学与技术"
            }
        ],
        works: [
            {
                company: "中国金融认证中心",
                position: "项目经理"
            }
        ]
    }
    '''

    if not geek:
        return False

    # 求职非工程师岗位
    expectPositionName = geek.get('expectPositionName', None)
    if expectPositionName:
        positionCategory = positionMap.get(expectPositionName, None)
        if not positionCategory:
            print('非技术同学: ', expectPositionName)
            return False
        if positionCategory in beta_positions:
            print('求职职位不匹配: ', positionCategory)
            return False

    edus = geek.get('edus', [])
    target_school = False
    for edu in edus:
        if edu.get('degree', 'unkown') in beta_degrees:
            print('学历不满足要求: ', edu.get('degree', 'unkown'))
            return False
        for school_dc in filters.school_dc:
            if edu.get('school', 'unkown') in school_dc:
                target_school = True
    if target_school:
        return True

    works = geek.get('works', [])
    for work in works:
        for com_dc in filters.company_dc:
            company = work.get('company', 'unknown')
            if company in com_dc or com_dc in company:
                return True

    print('无亮点: ', geek)
    return False


def geek_info_mapper(geek):
    '''
        从推荐的人的信息，转换成filter所需要的标准化信息
        return: 参见geeks_filter输入
    '''
    card = geek.get('geekCard')

    if not card:
        return None

    edus = list(map(lambda x: ({
        "degree": x.get('degreeName'),
        "school": x.get('school'),
        "major": x.get('major')
    }), card.get('geekEdus', [])))
    works = list(map(lambda x: ({
        "company": x.get('company'),
        "position": x.get('positionCategory')
    }),  card.get('geekWorks', [])))

    expectPositionName = card.get('expectPositionName', 'unknown')
    return {
        "expectPositionName": expectPositionName,
        "edus": edus,
        "works": works
    }

def detail_info_mapper(geek):
    if not geek:
        return None
    expectPositionName = geek.get('position', 'unknown')
    edus = list(map(lambda x: ({
        "degree": x.get('degree'),
        "school": x.get('school'),
        "major": x.get('major')
    }), geek.get('eduExpList', [])))

    works = list(map(lambda x: ({
        "company": x.get('company'),
        "position": x.get('positionName')
    }),  geek.get('workExpList', [])))

    return {
        "expectPositionName": expectPositionName,
        "edus": edus,
        "works": works
    }

session_file = './.session'
def load_session():
    if os.path.exists(session_file):
        with open(session_file, 'r') as file:
            content = file.read()
            return content.split()
    return None
def save_session(uid, user_id, token, client_id):
    with open(session_file, 'w+') as file:
        file.write(' '.join([uid, user_id, token, client_id]))


def random_sleep(min_time = 2, max_time = 15):
    interval = random.random() * (max_time - min_time)
    sec =  min(max(min_time, math.ceil(interval)), max_time)
    logger.info('\n sleep for %s seconds...\n' % ( sec))
    time.sleep(sec)


class Bot(BossBot):
    people = PeopleBot(logger)
    def auto_process(self, geek_id, securityId = ''):
        geek_id = str(geek_id)
        if not (geek_id in self.geek_feeds):
            if securityId:
                geek_data = self.get_geek_data(geek_id, securityId)
                self.geek_feeds[geek_id] = geek_data
            else:
                self.get_geek_feeds()
        geek = self.geek_feeds[geek_id]
        if not geek:
            return
        if geek.get('finished'):
            print("==========候选人已经处理过了: ", name)
            return
        name = geek.get('name')
        position = geek.get('position')
        print("==========处理候选人: ", name, "  ===求职期望:", position , "========", geek)
        messages = bot.get_geek_msgs(geek_id)
        infos = bot.brief_msgs_info(messages)
        print(infos)
        allmsgs = json.dumps(messages, ensure_ascii=False)
        enter = "\n"
        msg_text = enter.join(list(map(lambda x: x.get('pushText', ''), messages)))
        print(msg_text)
        first_greeting_text = "方便发一份简历吗？"
        second_greeting_text = "我们团队这有多个岗位可以按需匹配"
        has_first_greeting = first_greeting_text in allmsgs

        if not infos.get('is_my_text_msg') and not infos.get('is_resume') and not has_first_greeting:
            bot.send_message_geek(geek_id, first_greeting_text)
            random_sleep(2, 5)
            bot.send_message_geek(geek_id, second_greeting_text)
            random_sleep(1, 5)
            bot.request_geek_resume(geek_id)
        elif not infos.get('is_resume') and not infos.get('is_my_request_resume_msg'):
            bot.request_geek_resume(geek_id)

        if (not infos.get('is_resume')) and infos.get('is_geek_resume_request'):
            bot.accept_geek_resume(geek_id)
        if infos.get('is_resume'):
            #bot.send_message_geek(geek_id, "收到")
            bot.download_geek_resume(geek_id)
    def on_get_geek_resume(self, data, geek_id, msg, name):
        print('-----------get geek resume ----', geek_id, name)
        random_sleep(4, 10)
        print('-----------download geek resume ----', geek_id, name)
        self.download_geek_resume(geek_id)

    def on_text_message(self, data, uid, msg, securityId):
        '''
        文本 消息回调函数。
        :return:
        '''
        print('收到文字消息, 内容： ' + msg)
        #self.send_message_geek(uid, "你好")
        random_sleep(4, 10)
        self.auto_process(uid, securityId)
    def on_geek_greeting(self, data, uid, mid, securityId):
        print('招呼信息, 内容： ', securityId, data)
        random_sleep(4, 10)
        self.auto_process(uid, securityId)

    def on_request_resume_message(self, data, boss_id, mid):
        '''
        请求发送简历 消息回调函数
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param mid: 消息id，如果需要同意或者拒绝，需要此id
        :return:
        '''
        print('收到boss:%s,请求发送一份简历!' % boss_id)
        # 同意发送简历
        self.accept_resume(boss_id, mid, self.resumes[0]['resumeId'])

    def on_request_send_geek_resume(self, data, geek_id, mid):

        print('收到geek:%s,请求发送一份简历!' % geek_id)
        random_sleep(2, 4)
        self.accept_geek_resume(geek_id, mid)
        print('同意geek:%s,发送简历' % geek_id)

    def on_download_geek_resume(self, geek_id, filename, geek_data):
        geek_id = str(geek_id)

        geek = self.geek_feeds.get(geek_id)
        geek['finished'] = True
        print('====简历下载完毕，过滤中：', filename, geek_data)
        finnal_filter_result = geeks_filter(detail_info_mapper(geek_data))
        is_part_time = False
        if '实习' in filename or '应届' in filename:
            is_part_time = True
        # 对实习生网开一面
        if not finnal_filter_result and not is_part_time:
            print('====候选人被过滤了，暂不推荐到people: ', geek_data)
            return
        print('======开始内推======', filename)
        job_id = map_job(filename)
        if job_id:
            self.people.process_resume(filename, job_id)
        else:
            print('=====没有匹配的job', filename)

    def on_connect(self, client, userdata, flags, rc):
        '''
        websocket连接成功回调函数。
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        '''
        print("websocket 连接成功！")

def greeting(bot, max_page = 1):
    logger.info("\n==========开始打招呼了：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # 去寻找候选人打招呼
    print('职位：', bot.job_ids)
    can_greeting_today = True
    page = 1
    while page <= max_page and can_greeting_today:
        if not can_greeting_today:
            print('终止打招呼了')
            break;

        for job_id in bot.job_ids:
            geeks = bot.get_geeks(job_id, page)

            print("过滤前牛人:", len(geeks))

            targets = list(filter(lambda geek: (
                geek.get('haveChatted') == 0 and geeks_filter(geek_info_mapper(geek))
            ), geeks))

            print("过滤牛人剩余:", len(targets))
            for target in targets:
                can_greeting_today = bot.greeting_geek(target.get('encryptGeekId'))
                if not can_greeting_today:
                    break;
                random_sleep(10, 20)
        page = page + 1

def timed_greeting(interval, bot, max_page = 1, head = True):
    hour = time.localtime().tm_hour
    if hour >= 23 or hour <= 9:
        print('休息时间，不启动')
        bot.release_data()
        return
    if head:
        threading.Timer(1, greeting, (bot, max_page )).start()
    else:
        greeting(bot)

    threading.Timer(interval, timed_greeting, (interval, bot, max_page, False)).start()

def process_last_feeds(bot, max = 50):
    # 处理已经打招呼的
    bot.get_geek_feeds(1, max)
    for geek_id in list(bot.geek_feeds.keys()):
        bot.auto_process(geek_id)
        random_sleep(4, 10)

if __name__ == '__main__':

    bot = Bot(logger)
    bot.people.login()

    # 免扫码登陆，需要先通过扫码登陆，拿到对应账号信息。因为长期有效所以记录下来，直接使用。
    sessions = load_session()
    [uid, user_id, token, client_id] = [None, None, None, None]
    if sessions and len(sessions) >= 4:
        [uid, user_id, token, client_id] = sessions

    if uid and user_id and token:
        bot.login(uid, user_id, token, client_id)
    else:
        bot.login()
    bot.start()

    save_session(bot.uid, bot.user_id, bot.token, bot.client_id)

    # 处理已经打招呼的
    process_last_feeds(bot, 50)

    # #打招呼, 2小时一次
    timed_greeting(2 * 60 * 60, bot, 5)
