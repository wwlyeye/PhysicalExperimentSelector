# -*- coding: utf-8 -*-
import time
import requests
import threading
from datetime import datetime

from core import ocr
from core.log import logger
from core.storage import config, Session

# 常量
url = config.net['url']
ua = config.net['user-agent']

# 全局变量
running = True


class Robber:
    def __init__(self, session: requests.Session):
        if str(config.target['type']) == '0':
            type_code = '0'
            type_str = 'bas'  # 基物实验上，这里是bas
            # type_str = 'adv' # 基物实验下，这里是adv
        else:
            type_code = '1'
            type_str = 'aut'  # 基物实验上，这里是aut
            # 基物实验下，不知道是什么

        self.rob_params = {'type': type_code, 'step': '3', 'eid': type_str + config.target['week']}
        self.rob_data = {'Result': config.target['course']}

        self.session = session

    @property
    def token(self):
        return self.session.cookies.get('PHPSESSID')

    def rob(self):
        t = threading.Thread(target=self._rob)
        t.start()
        return t

    def _rob(self):
        global running
        t0 = datetime.now()
        resp = self.session.post(url + 'elect.php', self.rob_data, params=self.rob_params)
        t1 = datetime.now()
        html = resp.content.decode('gb2312')
        if html.find("你还没有登录，无权访问。") != -1:
            logger.fatal("[token {}][begin {}][end {}][elapse {}] Not login".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            return False
        if html.find("还没做吧？！") != -1:
            logger.info("[token {}][begin {}][end {}][elapse {}] Early".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            return False
        if html.find("该组已经选满。请重试！") != -1:
            # 选课不可能进行，停止接下来的抢课进程
            logger.warning("[token {}][begin {}][end {}][elapse {}] Full".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            running = False
            return False
        if html.find("此题目在这个时间段没有开放") != -1:
            # 选课不可能进行，停止接下来的抢课进程
            logger.error("[token {}][begin {}][end {}][elapse {}] Lesson not open".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            return False
        if html.find("三天内课表已冻结，请换个时间段!") != -1:
            # 选课不可能进行，停止接下来的抢课进程
            logger.error("[token {}][begin {}][end {}][elapse {}] Lesson expired".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            running = False
            return False
        if html.find("恭喜你，选课成功！") != -1:
            # 选课完成，停止接下来的抢课进程
            logger.warning("[token {}][begin {}][end {}][elapse {}] Success".format(
                self.token[:5],
                t0.strftime("%M:%S.%f")[:-3],
                t1.strftime("%M:%S.%f")[:-3],
                "{:.3f}".format((t1 - t0).total_seconds())))
            running = False
            return True

        logger.error("[token {}][begin {}][end {}][elapse {}] Unknown error".format(
            self.token[:5],
            t0.strftime("%M:%S.%f")[:-3],
            t1.strftime("%M:%S.%f")[:-3],
            "{:.3f}".format((t1 - t0).total_seconds())))
        # print(html)


class RobberManager:
    def __init__(self):
        self.robbers = []
        self.sessions = []
        self.login()

    @property
    def login_data(self):
        return {
            'txtUid': config.account['username'],
            'txtPwd': config.account['password'],
            'txtChk': self.checkcode
        }

    def _login(self):
        for retry in range(3):
            session = requests.session()
            session.headers['User-Agent'] = ua
            session.get(url + 'index.php')
            response = session.get(url + 'checkcode.php')
            img_bin = response.content
            o = ocr.OCR()
            self.checkcode = o.number_from_bin(img_bin)
            if not self.checkcode:
                logger.info("Failed to get checkcode, retry:{}".format(retry + 1))
                continue
            session.post(url + 'login.php', data=self.login_data)
            resp = session.get(url + 'elect.php')
            if resp.status_code == 200 and resp.content.decode('gb2312').find('你还没有登录，无权访问。') == -1:
                logger.info("Login succeed")
                return session
            else:
                logger.info("Login failed, retry:{}".format(retry + 1))
                continue
        return None

    @staticmethod
    def test_available(session_id):
        session = requests.session()
        session.headers['User-Agent'] = ua
        session.cookies.set('PHPSESSID', session_id)
        resp = session.get(url + 'elect.php')
        if resp.status_code == 200 and resp.content.decode('gb2312').find('你还没有登录，无权访问。') == -1:
            logger.info("Session is available: {}...".format(session_id[0:10]))
            return session
        else:
            logger.info("Session is not available: {}...".format(session_id[0:10]))
            return None

    def login(self):
        logger.warning("begin to get enough sessions")
        session_ids = Session.load()
        sessions = []
        for sid in session_ids:
            session = self.test_available(sid)
            if session:
                sessions.append(session)
            if len(sessions) >= config.speed['number-of-clients']:
                break
        load_number = len(sessions)
        total_retry = 0
        total_retry_max = 5
        try:
            while len(sessions) < config.speed['number-of-clients'] and total_retry < total_retry_max:
                session = self._login()
                if session:
                    sessions.append(session)
                else:
                    total_retry += 1
        except KeyboardInterrupt:
            Session.dump([x.cookies.get('PHPSESSID') for x in sessions])
            exit(1)
        got = len(sessions)
        new_number = got - load_number
        logger.warning(
            "Wants {}, got {}, loaded {}, new {}, total retry {}".format(config.speed['number-of-clients'], got,
                                                                         load_number, new_number, total_retry))
        Session.dump([x.cookies.get('PHPSESSID') for x in sessions])
        self.sessions = sessions

    def logout(self):
        for session in self.sessions:
            session.get(url + 'logout.php')

    def rob(self):
        global running
        running = True
        self.robbers = [Robber(x) for x in self.sessions]
        interval = config.speed['interval']
        max_running_time = config.speed['max-running-time']
        start_at = time.time()
        threads = []
        try:
            while max_running_time == 0 or time.time() - start_at < max_running_time:
                for robber in self.robbers:
                    if not running:
                        logger.info("Completed")
                        logger.info("Waiting for running threads to finish")
                        for t in threads:
                            t.join()
                        return
                    t = robber.rob()
                    threads.append(t)
                    time.sleep(interval)
            logger.info("Time Limit Exceeded")
            logger.info("Waiting for running threads to finish")
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            logger.info("Interrupted")
            exit(1)


# debug
if __name__ == '__main__':
    r = RobberManager()
    r.rob()
