# Author = 'Vincent FUNG'
# Create = '2017/09/07'

import logging
import sys
import io

# +++++++++++++++++++++++++++
# 1) Data: log.info(' %-20s ]-[ %s ]-[ %s ]-[ Data: [ receive:%.2f KB/s , send:%.2f KB/s ] ' % (
#                   func_name, py_pid, indicator, data_msg)
# 2) info: log.info(' %-20s ]-[ %s ]-[ %s ]-[ Got previous network data of uid %s . . . ' % (
#                   func_name, py_pid, device_id, process_uid))
# 3) Err : log.error(' %-20s ]-[ Memory usage source data can not match any data type ! ! ! ' % _func_name)
# +++++++++++++++++++++++++++

def setup_io():
    sys.stdout = sys.__stdout__ = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = sys.__stderr__ = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)


class Logger:
    """Logger class.
    """
    def __init__(self, path, logger, clevel=logging.INFO, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(logger)        # 获取名为logger的logger
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            '[ %(asctime)s ]-[ %(name)-20s ]-[ %(levelname)-8s ]: -> [ %(message)s ]')               # '%(asctime)s [%(levelname)s] %(filename)s line:%(lineno)d: %(message)s'
        # console logger
        shell_stream = logging.StreamHandler()
        shell_stream.setFormatter(fmt)
        shell_stream.setLevel(clevel)
        # file logger
        file_stream = logging.FileHandler(path)
        file_stream.setFormatter(fmt)
        file_stream.setLevel(Flevel)
        self.logger.addHandler(shell_stream)
        self.logger.addHandler(file_stream)
        setup_io()

    @staticmethod
    def get_function_name():
        """Get the name of the calling method.

        Returns:
            [String] -- [Method name]
        """
        return sys._getframe().f_back.f_code.co_name

    def debug(self, message):
        """Log the debug level.

        Arguments:
            message {String} -- [Log content.]
        """
        self.logger.debug(str(message))

    def info(self, message):
        """Log the info level.

        Arguments:
            message {String} -- [Log content.]
        """
        self.logger.info(str(message))

    def warn(self, message):
        """Log the warning level.

        Arguments:
            message {String} -- [Log content.]
        """
        self.logger.warning(str(message))

    def error(self, message):
        """log the error level.

        Arguments:
            message {String} -- [Log content.]
        """
        self.logger.error(str(message))

    def cri(self, message):
        """log the critical level.

        Arguments:
            message {String} -- [Log content.]
        """
        self.logger.critical(str(message))
