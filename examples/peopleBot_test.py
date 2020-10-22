# -*- coding: utf-8 -*-
import json
import logging
import time
import os
import re
from peoplebot import PeopleBot
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()

jobs = {
  'HR': ['6843364252502837512', '6843364252502837512'],
  '服务端': ['6860361408367315214', '6704443756197710094'],
  '后端': ['6860361408367315214', '6704443756197710094'],
  'Android': ['6704530394017958148', '6704433460473235726'],
  'IOS': ['6704579151484946692', '6704579127824877831'],
  '前端': ['6704579151308785928', '6704552316768356615'],
  'Rust': ['6704534498622572807', '6704463170729150724'],
  'C工程师': ['6704534498622572807', '6704463170729150724'],
  '数据': ['6721890202450659592', '6750951560294959374'],
  'AI': ['6717472122249152782', '6753920635681900814'],
  '测试': ['6860742208796018958', '6870404247897950477']
}

if __name__ == '__main__':
  print('start people bot')
  bot = PeopleBot(logger)
  bot.login()
  path = './resumes/' + time.strftime('%Y-%m-%d',time.localtime(time.time()))
  logger.info(path)
  files = os.listdir(path)
  logger.info(len(files))
  for file in files:
    if not os.path.isdir(file):
      time.sleep(3)
      for key in jobs:
        if key in file:
          idx = 0
          if '实习' in file or '应届生' in file:
            idx = -1
          bot.process_resume(path + '/' + file, jobs[key][idx])