# Author = 'Vincent FUNG'
# Create = '2017/09/06'

import subprocess

import sys

try:
    import logger
except ModuleNotFoundError:
    import http_websocket.logger
log = logger.Logger('runtimelog/r.log', 'SubProcessBase')


def popen_judge(popen_obj, method_name, parameters):
    if popen_obj.returncode == 0:
        if popen_obj.stdout and not popen_obj.stderr:
            log.debug(' %-20s ]-[ Return: %s' % (method_name, popen_obj.stdout))
            return popen_obj
        else:
            return 1
    elif popen_obj.returncode != 0 and popen_obj.stderr:
        log.cri(
            ' %-20s ]-[ System cmd execution err: %s, code:%d, incoming parameters: %s' % (
                method_name, popen_obj.stderr, popen_obj.returncode, parameters))
        return False
    else:
        log.error(
            ' %-20s ]-[ Unexpected exception: %s, code:%d' %
            (method_name, popen_obj.stderr.decode(), popen_obj.returncode))
        return False


class SubProcessBase:
    def __init__(self):
        pass

    @staticmethod
    def sub_procs_run(**args):

        _func_name = sys._getframe().f_back.f_code.co_name
        log.debug(' %-20s ]-[ Parameters in: %s' % (_func_name, args))
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
