# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import hashlib
from urllib import parse
from urllib import request
import datetime
import time
import queue

try:
    from logger import Logger
    from subproc import SubProcessBase
    from parse_crash_log import CrashParser
except ModuleNotFoundError as e:
    from http_websocket.logger import Logger
    from http_websocket.subproc import SubProcessBase
    from http_websocket.parse_crash_log import CrashParser

log = Logger('/var/log/CrashParser.log', 'GetCrashLog')

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
        :return: crash_id, List object.
        """
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
            log.info(' %-20s ]-[ Crash id list from server. \n%s' % (log.get_function_name(), ', '.join(task_list)))
            if task_list:
                return eval(task_list)
        except request.HTTPError as httperror:
            times -= 1
            log.error(' %-20s ]-[ Get crash ids from server error. info: %s' % (log.get_function_name(), httperror.info()))
            if times != 0:
                time.sleep(2)
                self.get_task_list(version, date)

    def get_crash_log(self, version, date=yesteday):
        """
        Get aim crash_id's content from web API.
        :return: Crash log information. Bytes object
        """
        task_ids = self.get_task_list(version=version, date=date)
        if task_ids:
            for task_id in task_ids:
                param = {'row': task_id}

                parm_encode = parse.urlencode(param).encode('utf-8')

                crash_page = request.Request(
                    url=self.read_ids_url,
                    data=parm_encode
                )

                crash_content = request.urlopen(crash_page).read()
                yield task_id, crash_content
