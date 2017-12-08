# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import hashlib
from urllib import parse
from urllib import request
import datetime
import time
import queue

import os

try:
    from logger import Logger
    from subproc import SubProcessBase
    from parse_crash_log import CrashParser
    from parser_exception import ReadFromServerException
except ModuleNotFoundError as e:
    from http_websocket.logger import Logger
    from http_websocket.subproc import SubProcessBase
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.parser_exception import ReadFromServerException

log_file = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
log = Logger(log_file, 'GetCrashLog')

yesteday = str(datetime.date.today() - datetime.timedelta(1))


class GetCrashInfoFromServer(object):
    """docstring for GetCrashInfoFromServer"""

    def __init__(self):
        super(GetCrashInfoFromServer, self).__init__()
        self.sec_key = '8HTm)NZ[K=I0Ju!L%a@Ua!#g29ZPFgm9'
        self.domain = 'http://gdata.linkmessenger.com'
        self.api = 'index.php/Admin/Api'
        self.method_get = 'getAppError'
        self.method_read = 'appErrorInfo'
        self.get_ids_url = '/'.join([self.domain, self.api, self.method_get])
        self.read_ids_url = '/'.join([self.domain, self.api, self.method_read])
        self.que = queue.Queue()
        self.md5 = hashlib.md5()
        self.sproc = SubProcessBase()

    def get_md5(self, date):
        """
        Compute sign key to access crash log API
        :param date: '%Y-%m-%d' format string. Default is yesterday
        :return: sign key, String object
        """
        md5 = hashlib.md5()
        md5.update((self.sec_key + str(date)).encode())
        return md5.hexdigest().lower()

    def get_task_list(self, version, date):
        """
        Get crash_id from web API
        :return: List object. Crash ids.
        """
        # Define retry times.
        times = 4
        params = {
            'day': date,
            'ver': version,
            'sign': self.get_md5(date)
        }

        url_params = parse.urlencode(params).encode('utf-8')

        list_params = request.Request(
            url=self.get_ids_url,
            data=url_params
        )
        try:
            task_list = request.urlopen(list_params).read()
            log.info(' %-20s ]-[ Crash id list from server: \n%s' % (log.get_function_name(), str(task_list)))
            # Validation data validity.
            if len(task_list) > 10:
                # Source data transition to list type.
                return eval(task_list)
        # Retry for HTTP 404 temporary
        except request.HTTPError as httperror:
            times -= 1
            log.error(' %-20s ]-[ Get crash ids from server error. info: %s' % (log.get_function_name(), httperror.info()))
            if times != 0:
                time.sleep(2)
                self.get_task_list(version, date)

    def get_crash_log(self, task_id):
        """
        Get crash log from server.
        :param task_id: one id for API.
        :return: String object.
        """
        log.debug(' %-20s ]-[ Get crash log with ID: %s' % (log.get_function_name(), task_id))
        param = {'row': task_id}

        parm_encode = parse.urlencode(param).encode('utf-8')

        crash_page = request.Request(
            url=self.read_ids_url,
            data=parm_encode
        )

        crash_content = request.urlopen(crash_page).read()
        log.debug(' %-20s ]-[ Get crash log with id(%s) done!' % (log.get_function_name(), task_id))
        return crash_content

    def gen_task_log(self, version, date=yesteday):
        """
        Get aim crash_id's content from web API.
        :param version: Version information from task_manager.
        :param date: Which crash of day want to get. Default is yesterday.
        :return:
        """
        if isinstance(version, str):
            # Get crashes
            task_ids = self.get_task_list(version=version, date=date)
            if not task_ids:
                raise ReadFromServerException('No crash can be read of the last 3 versions.')
            else:
                for task_id in task_ids:
                    _crash_log = self.get_crash_log(task_id)
                    yield task_id, _crash_log
        else:
            raise TypeError('The type error of variable "version". Expected %s. But %s ' % (type(str()), type(version)))
