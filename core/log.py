# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import os

logger = logging.getLogger("selector")
logger.setLevel("INFO")
dirname = 'log'
if not os.path.exists(dirname):
    os.mkdir(dirname)
time_str = datetime.now().strftime("%m-%d")
filepath = os.path.join(dirname, time_str + ".log")
file_handler = logging.FileHandler(filename=filepath, mode="a", encoding="utf-8")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] (%(threadName)s) %(message)s")
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# debug
if __name__ == '__main__':
    from datetime import datetime
    import time
    from threading import Thread


    def billy(logger):
        logger.warning("oh my shoulder")


    t0 = datetime.now()
    time.sleep(0.5)
    t1 = datetime.now()
    logger.info("[begin {}][end {}][elapse {}]".format(t0.strftime("%M:%S.%f")[:-3],
                                                       t1.strftime("%M:%S.%f")[:-3],
                                                       "{:.3f}".format((t1 - t0).total_seconds())))
    t = Thread(target=billy, args=(logger,))
    t.start()
