# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import hashlib
from urllib import parse
from urllib import request
import datetime
import os
import queue
try:
    from subproc import SubProcessBase
    from parse_crash_log import CrashParser
except ModuleNotFoundError as e:
    from http_websocket.subproc import SubProcessBase
    from http_websocket.parse_crash_log import CrashParser

yesteday = str(datetime.date.today() - datetime.timedelta(1))

class GetCrashInfoFromServer(object):
    """docstring for GetCrashInfoFromServer"""

    def __init__(self, version, date=yesteday):
        super(GetCrashInfoFromServer, self).__init__()
        self.sec_key = '8HTm)NZ[K=I0Ju!L%a@Ua!#g29ZPFgm9'
        self.domain = 'http://gdata.linkmessenger.com'
        self.api = 'index.php/Admin/Api'
        self.method_get = 'getAppError'
        self.method_read = 'appErrorInfo'
        self.date = date
        self.version = version
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
        self.md5.update((self.sec_key + str(date)).encode())
        return self.md5.hexdigest().lower()

    def get_task_list(self):
        """
        Get trac_id from web API
        :return: trac_id, List object.
        """
        params = {
            'day': self.date,
            'ver': self.version,
            'sign': self.get_md5(self.date)
        }

        url_params = parse.urlencode(params).encode('utf-8')

        list_params = request.Request(
            url=self.get_ids_url,
            data=url_params
        )
        task_list = request.urlopen(list_params).read()

        return eval(task_list)

    def get_crash_log(self):
        """
        Get aim trac_id's content from web API.
        :return: Crash log information. Bytes object
        """
        task_ids = self.get_task_list()
        crash_content = ''
        for i in task_ids:
            yield crash_content
            param = {'row': i}

            parm_encode = parse.urlencode(param).encode('utf-8')

            crash_page = request.Request(
                url=self.read_ids_url,
                data=parm_encode
            )

            crash_content = request.urlopen(crash_page).read()

    def run(self):
        for i in self.get_crash_log():
            print(i)


gcsi = GetCrashInfoFromServer(version='V1.9.5 (11311) [正式版]')
gcsi.run()