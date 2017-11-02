# Author = 'Vincent FUNG'
# Create = '2017/09/07'

import logging


# call_name = inspect.stack()[1][3]
# func_name = sys._getframe().f_code.co_name
import sys

# +++++++++++++++++++++++++++
# 1) Data: log.info(' %-20s ]-[ %s ]-[ %s ]-[ Data: [ receive:%.2f KB/s , send:%.2f KB/s ] ' % (
#                   func_name, py_pid, indicator, data_msg)
# 2) info: log.info(' %-20s ]-[ %s ]-[ %s ]-[ Got previous network data of uid %s . . . ' % (
#                   func_name, py_pid, device_id, process_uid))
# 3) Err : log.error(' %-20s ]-[ Memory usage source data can not match any data type ! ! ! ' % _func_name)
# +++++++++++++++++++++++++++


class Logger:
    def __init__(self, path, logger, clevel=logging.INFO, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            '[ %(asctime)s ]-[ %(name)-20s ]-( %(levelname)-8s ]: -> [ %(message)s ]')
        # console logger
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        # file logger
        fh = logging.FileHandler(path)
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    @staticmethod
    def get_function_name():
        return sys._getframe().f_back.f_code.co_name

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)
