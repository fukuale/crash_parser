# Author = 'Vincent FUNG'
# Create = '2017/09/24'

'''
http://gdata.linkmessenger.com/index.php/Admin/Api/getAppError?day=2017-09-20&ver=V1.9.4+%2811297%29+%5B%E6%AD%A3%E5%BC%8F%E7%89%88%5D&sign=a484b003f9a87cad9ac03390f5201b92
$skey = '8HTm)NZ[K=I0Ju!L%a@Ua!#g29ZPFgm9';
        $sign = I('sign');
        $day = I('day');
        if ($sign != md5($skey.$day)) {
            exit();
        }

http://gdata.linkmessenger.com/index.php/Admin/Api/appErrorInfo?row=if-0-1505981280967

'''
import hashlib
from urllib import parse
from urllib import request
import datetime
import os
import queue
from subproc import SubProcessBase


class GetCrashInfoFromServer(object):
    """docstring for GetCrashInfoFromServer"""

    def __init__(self):
        super(GetCrashInfoFromServer, self).__init__()
        self.sec_key = '8HTm)NZ[K=I0Ju!L%a@Ua!#g29ZPFgm9'
        self.domain = 'http://gdata.linkmessenger.com'
        self.api = 'index.php/Admin/Api'
        self.method_get = 'getAppError'
        self.method_read = 'appErrorInfo'
        self.date = str(datetime.date.today() - datetime.timedelta(4))
        self.version = 'V1.9.5 (11311) [正式版]'
        self.get_ids_url = '/'.join([self.domain, self.api, self.method_get])
        self.read_ids_url = '/'.join([self.domain, self.api, self.method_read])
        self.que = queue.Queue()
        self.md5 = hashlib.md5()
        self.sproc = SubProcessBase()

    def get_md5(self, date):
        self.md5.update((self.sec_key + str(date)).encode())
        return self.md5.hexdigest().lower()

    def get_task_list(self):
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

    def splicing_url(self):
        task_ids = self.get_task_list()
        url = ''
        for i in task_ids:
            yield url
            param = {'row': i}

            parm_encode = parse.urlencode(param).encode('utf-8')

            crash_page = request.Request(
                url=self.read_ids_url,
                data=parm_encode
            )

            url = request.urlopen(crash_page).read()

    def run(self):
        for i in self.splicing_url():
            print(i)


gcsi = GetCrashInfoFromServer()
gcsi.run()