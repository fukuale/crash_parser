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
        self.md5 = hashlib.md5()
        self.domain = 'http://gdata.linkmessenger.com'
        self.api = 'index.php/Admin/Api'
        self.get_list = 'getAppError'
        self.read_info = 'appErrorInfo'
        self.date = str(datetime.date.today() - datetime.timedelta(8))
        self.version = 'V1.9.5 (11311) [正式版]'
        self.sproc = SubProcessBase()
        self.get_ids_url = '/'.join([self.domain, self.api, self.get_list])
        self.read_ids_url = '/'.join([self.domain, self.api, self.read_info])
        self.que = queue.Queue()

    def get_md5(self, date):
        self.md5.update((self.sec_key + str(date)).encode())
        return self.md5.hexdigest().lower()

    def splicing_url(self):
        params = {
            'day': self.date,
            'ver': self.version,
            'sign': self.get_md5(self.date)
        }

        url_params = parse.urlencode(params).encode('utf-8')

        get_url = '/'.join([self.domain, self.api, self.get_list])
        read_url = '/'.join([self.domain, self.api, self.read_info])

        print('get_url', get_url)
        print('read_url', read_url)

        list_temp = request.Request(
            url=get_url,
            data=url_params
        )
        data = request.urlopen(list_temp).read()

        url_row = [parse.urlencode({'row': x})for x in eval(data)]
        # url_row = [lambda x: parse.urlencode({'row': x}).encode('utf-8'), eval(data)] #useless??
        # print(url_row)
        for i in url_row:
            print(read_url + '?' + i)
            _data = request.urlopen(read_url + '?' + i).read()
        #
        #     self.que.put(_data)
            print(_data.decode())
        #     print(_temp)
        #     break
        # print(self.que.get())




        # id_list = self.sproc.sub_procs_run(cmd='curl %s' % get_url)
        # id_list = eval(id_list)
        # print('id_list', type(id_list), id_list)
  #       for i in id_list:
		# crash_data = self.sproc.sub_procs_run('curl %s' % read_url)




if __name__ == '__main__':
    gcis = GetCrashInfoFromServer()
    gcis.splicing_url()

