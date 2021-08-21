"""
精准倒计时库
在邻近终点时间是会采用轮询来倒计时，尽可能避免时间偏差
"""
import datetime
import time
from core.log import logger


def count_down(callback, sche: datetime.datetime):
    logger.debug("Start to count down")
    counting = datetime.timedelta(seconds=10)
    delta = datetime.timedelta(seconds=1)
    while counting.total_seconds() >= 0:
        now = datetime.datetime.now()
        if sche - now < counting:
            logger.info("Counting down: {}".format(counting.seconds))
            counting -= delta
    callback()


def run_at_spec_time(callback, sche: datetime.datetime):
    now = datetime.datetime.now()
    sleep_time = (sche - now).total_seconds() - 11
    if sleep_time > 0:
        time.sleep(sleep_time)
    count_down(callback, sche)


if __name__ == '__main__':
    def foo():
        n = datetime.datetime.now()
        print("Executed at", n)


    now = datetime.datetime.now()
    print("Now: ", now)
    # sche = now.replace(hour=23, minute=59, second=59, microsecond=0)
    sche = now.replace(second=59, microsecond=0)
    print("Scheduled time: ", sche)

    run_at_spec_time(foo, sche)
