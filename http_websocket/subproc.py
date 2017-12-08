# Author = 'Vincent FUNG'
# Create = '2017/09/06'

import subprocess

import sys

import os

try:
    from logger import Logger
except ModuleNotFoundError:
    from http_websocket.logger import Logger

log_file = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
log = Logger(log_file, 'SubProcessBase')


def popen_judge(popen_obj, method_name, parameters):
    if popen_obj.returncode == 0:
        log.debug(' %-20s ]-[ Return: %s' % (method_name, popen_obj.stdout))
        return popen_obj
    elif popen_obj.returncode != 0 and popen_obj.stderr:
        log.cri(
            ' %-20s ]-[ System cmd execution err: %s, code:%s, incoming parameters: %s' % (
                method_name, popen_obj.stderr, str(popen_obj.returncode), str(parameters)))
        if 'curl' in parameters.values():
            return popen_obj
        return False
    else:
        log.cri(
            ' %-20s ]-[ Unexpected exception: %s, code:%d' %
            (method_name, popen_obj.stderr.decode(), popen_obj.returncode))
        return False


class SubProcessBase:
    def __init__(self):
        pass

    @staticmethod
    def sub_procs_run(**args):

        _func_name = sys._getframe().f_back.f_code.co_name
        log.debug(' %-20s ]-[ Parameters in: %s' % (_func_name, str(args)))
        if args.__len__() == 1:
            _sub_result = subprocess.run(args['cmd'].encode(),
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=True)
            return popen_judge(_sub_result, _func_name, args)
        else:
            log.error(' %-20s ]-[ %s arg invalid!' % _func_name)
            pass
