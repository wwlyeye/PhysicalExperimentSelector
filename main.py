import datetime
from core.selector import RobberManager
from core.log import logger
from core import timer

DEBUG = False

if __name__ == '__main__':
    logger.info("Program started")

    now = datetime.datetime.now()
    # 在当天23:59:59时启动抢课进程
    rob_schedule = now.replace(hour=23, minute=59, second=59, microsecond=0)
    # 在抢课前5分钟刷新所有账号
    refresh_schedule = rob_schedule - datetime.timedelta(minutes=5)
    if DEBUG:
        refresh_schedule = now
        rob_schedule = now + datetime.timedelta(seconds=10)

    r = RobberManager()
    if refresh_schedule > now:
        timer.run_at_spec_time(r.login, refresh_schedule)
    timer.run_at_spec_time(r.rob, rob_schedule)
