# -*- coding: utf-8 -*-
import toml
import os
from core.log import logger

template = """\
[target]
# 0为实验选课 1为预约选课
type = "0"

# 为下面四项的和，当其为8位有效数字时覆盖下面四项
# course = "10710513"

# 课程代号(4位)
course-id = "1071"

# 选课周次(用0补齐至2位)
week = "05"

# x: 星期x
day-of-week = "1"

# 1: 早上, 2: 下午, 3: 晚上
time-of-day = "3"

[speed]
# 登录次数，增大登录次数可以无视排队机制，快速选上课
number-of-clients = 20

# 两次选课间的间隔(s) 该值不应低于0.1
interval = 0.1

# 最长运行时间(s)
max-running-time = 5

[account]
# 基物实验选课网用户名
username = ""
# 基物实验选课网密码
password = ""

# ocr部分介绍详见README.md
[ocr]
local = true
appid = ""
api-key = ""
secret-key = ""

[net]
# 选课网址
url = "http://115.25.136.17:9000/"
# Windows10 Chrome 的 User-Agent
user-agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
"""


class Config:
    def __init__(self):
        self.filepath = 'config.toml'
        if not os.path.exists(self.filepath):
            self.generate_template()
            logger.warning("未发现配置文件'config.toml', 已生成模板，请进行相关配置后再次运行。")
            exit(1)
        self.load()

    def generate_template(self):
        with open(self.filepath, 'w') as fp:
            fp.write(template)

    def load(self):
        with open(self.filepath, 'r') as fp:
            cd = toml.load(fp)
        self.__dict__.update(cd)
        try:
            course = str(self.target['course'])
        except KeyError:
            course = ""
        if len(course) == 8 and course.isnumeric():
            self.target['course-id'] = course[0:4]
            self.target['week'] = course[4:6]
            self.target['day-of-week'] = course[6]
            self.target['time-of-day'] = course[7]
            logger.warning("已使用target.course覆盖分项设置")
        else:
            assert isinstance(self.target['course-id'], str) and \
                   isinstance(self.target['week'], str) and \
                   isinstance(self.target['day-of-week'], str) and \
                   isinstance(self.target['time-of-day'], str), "Config values for [target] must be strings"
            assert len(self.target['course-id']) == 4, "target.course-id must have the length of 4"
            assert len(self.target['week']) == 2, "target.week must have the length of 2"
            assert len(self.target['day-of-week']) == 1, "target.day-of-week must have the length of 1"
            assert len(self.target['time-of-day']) == 1, "target.time-of-day must have the length of 1"
        self.target['course'] = self.target['course-id'] + self.target['week'] + self.target['day-of-week'] + \
                                self.target['time-of-day']
        logger.warning("最终选课配置为: {}".format(self.target['course']))


config = Config()


class Session:
    filename = "session.txt"

    @staticmethod
    def load() -> list:
        if not os.path.exists(Session.filename):
            return []
        with open(Session.filename, "r") as fp:
            return [x.strip() for x in fp.readlines()]

    @staticmethod
    def dump(sessions: list):
        with open(Session.filename, "w") as fp:
            return fp.writelines([x + '\n' for x in sessions])
