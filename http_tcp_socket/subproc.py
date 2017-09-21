# Author = 'Vincent FUNG'
# Create = '2017/09/06'

import subprocess

import sys

import logger

log = logger.Logger('runtimelog/r.log', 'SubProcessBase')


def popen_judge(popen_obj, log_func_name, parameters):
    try:
        if popen_obj.returncode == 0 and popen_obj.stdout:
            log.debug(' %-20s ]-[ Return: %s' %
                      (log_func_name, popen_obj.stdout))
        elif popen_obj.returncode != 0:
            log.cri(
                ' %-20s ]-[ System cmd execution err: %s, code:%d, parameters in: %s' % (
                    log_func_name, popen_obj.stderr, popen_obj.returncode, parameters))
        elif popen_obj.stderr.decode():
            print('popen_obj.stdout', popen_obj.stdout)
            print('popen_obj.stderr', popen_obj.stderr)
            log.error(' %-20s ]-[ Mobile shell cmd execution err: %s' %
                      (log_func_name, popen_obj.stderr))
        elif not popen_obj.stdout.decode():
            log.error(
                ' %-20s ]-[ Mobile shell nothing to print out' % log_func_name)
        else:
            log.error(
                ' %-20s ]-[ Unexpected exception: %s, code:%d' %
                (log_func_name, popen_obj.stderr.decode(), popen_obj.returncode))
        return popen_obj
    except UnicodeDecodeError:
        log.cri(' %-20s ]-[ Result can not decode, check the resource data: %s ' %
                (log_func_name, popen_obj))


class SubProcessBase:

    def __init__(self):
        pass

    @staticmethod
    def sub_procs_run(**args):
        _func_name = sys._getframe().f_code.co_name
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
