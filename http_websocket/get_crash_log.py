# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import base64
import datetime
import hashlib
import os
import queue
import sys
import time
import http
from urllib import parse, request

from http_websocket.logger import Logger
from http_websocket.parser_exception import ReadFromServerException
from http_websocket.subproc import SubProcessBase

'''
sc_get_ids_url:
http://crec.streamcraft.com:95/noauth/apperror/getAppErrorIds
sc_get_log_url:
http://crec.streamcraft.com:95/noauth/apperror/getAppErrorByIds
获取某一天的日志
'''
logname = 'CrashLog' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.log'
LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', logname)
LOG = Logger(LOG_FILE, 'GetCrashLog')

YESTERDAY = str(datetime.date.today() - datetime.timedelta(1))


class GetCrashInfoFromServer(object):
    """
    Get crash info from server.
    """
    def __init__(self):
        super(GetCrashInfoFromServer, self).__init__()
        # Define for WeGamers
        self.sec_key = '8HTm)NZ[K=I0Ju!L%a@Ua!#g29ZPFgm9'
        self.wegamers_domain = 'http://gdata.linkmessenger.com'
        self.wegamers_api_dir = 'index.php/Admin/Api'
        self.wegamers_api_get_crash = 'appErrorInfo'
        self.api_get_ids = 'getAppError'
        self.wg_get_ids_url = '/'.join([self.wegamers_domain, self.wegamers_api_dir, self.api_get_ids])
        self.wg_get_log_url = '/'.join([self.wegamers_domain, self.wegamers_api_dir, self.wegamers_api_get_crash])
        
        # Define for ScreamCraft
        self.sc_domain = 'http://crec.streamcraft.com:95'
        self.sc_api_dir = 'noauth/apperror'
        self.sc_api_get_ids = 'getAppErrorIds'
        self.sc_api_get_log = 'getAppErrorByIds'
        self.sc_get_ids_url = '/'.join([self.sc_domain, self.sc_api_dir, self.sc_api_get_ids])
        self.sc_get_log_url = '/'.join([self.sc_domain, self.sc_api_dir, self.sc_api_get_log])

        # Common define.
        self.que = queue.Queue()
        self.md5 = hashlib.md5()
        self.sproc = SubProcessBase()

    def get_md5(self, data):
        """Compute sign key to access crash log API

        Arguments:
            date {String} -- [Date timestamp.]

        Returns:
            [String] -- [The MD5 of date.]
        """
        md5 = hashlib.md5()
        md5.update((self.sec_key + str(data)).encode())
        return md5.hexdigest().lower()

    def splicing_ids_url(self, version, date):
        """Splicing the url of http API
        
        Arguments:
            version {String} -- [The version from JIRA]
            date {String} -- [Date format string]
        
        Raises:
            ReadFromServerException -- [description]
        
        Returns:
            [type] -- [description]
        sc不支持获取某个版本号的崩溃日志，WG支持获取某个版本号的崩溃日志
        """
        # Define request for urlopen.
        _req = request.Request

        # Set the parameters for each project.

        # Set request parameters to body(normally) and request via method POST.
        if version[0] == 'WeGamers':
            # Body form set.
            params = {
                'day': date,
                'ver': version[-1],
                'sign': self.get_md5(date)
            }
            # parameters include the chinese characters. Need to encode with UTF-8.
            url_params = parse.urlencode(params).encode('utf-8')

            return request.Request(url=self.wg_get_ids_url, data=url_params, method='POST')

        # Set request parameters to headers and request via method GET.
        elif version[0] == 'GameLive':
            # Change the date format to %Y%m%d from %Y-%m-%d
            _strpdate = datetime.datetime.strftime(              #日期格式转化为字符串格式
                datetime.datetime.strptime(date, '%Y-%m-%d'),   #字符串格式转化为日期格式
                '%Y%m%d'
            )
            # Headers set.
            header = {
                'date': _strpdate,
                'sign': self.get_md5(_strpdate)
            }

            return request.Request(url=self.sc_get_ids_url, headers=header, method='GET')
        else:
            err = "Can't splicing the url." #%s" % params.__str__()
            raise ReadFromServerException(err)

    def get_task_list(self, version, date, platform, times=4, before=0):
        """Get crash_id from web API

        Arguments:
            version {String} -- [The version from JIRA]
            date {String} -- [Date timestamp.]

        Returns:
            [List] -- [The crash ids list.]
            id：a是安卓
            i是苹果 f是崩溃 c是common
        """
        
        try:
            # TODO: Http status 200 judge logic. to ensure the server still works.
            _req = self.splicing_ids_url(version=version, date=date)
            task_list = request.urlopen(_req).read()
            #LOG.info(task_list[1])
            # Validation data validity.

            # validation the first character is symbol "[". If it's, that could eval to list. if not, that's useless result.
            if task_list[0] == 91:
                _task_list = eval(task_list)
                #LOG.info(_task_list)
                # remove the id is not startswith 'if'. if=iOS Crash.
                _temp_list = list()
                for x in _task_list:
                    if not x.startswith(platform):
                        _temp_list.append(x)
                _task_list = list(set(_task_list).difference(_temp_list))
                #LOG.info(_task_list)
                # If len == 0. Try to get the the day before.
                if _task_list.__len__() != 0:
                    return _task_list
                elif _task_list.__len__() == 0 and not before:                #如果无数据，再去获取前一天的数据
                    before += 1
                    LOG.info(' %-20s ]-[ Crash id list from server: \n%s' % (LOG.get_function_name(), [_req.full_url, _req.data, _req.headers]))
                    new_date = str((datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(1)).date())          #strptime由字符串格式转化为日期格式
                    return self.get_task_list(version=version, date=new_date, before=before)
                elif _task_list.__len__() == 0 and before:
                    LOG.info(' %-20s ]-[ Crash id list from server: \n%s' % (LOG.get_function_name(), str(task_list)))
                    raise ReadFromServerException('Could not read crash list from server for the latest 2 days')
            raise ReadFromServerException('The data isn\'t the expeted type.')
        # Retry for HTTP 404 temporary and another exception.
        except request.HTTPError as httperror:
            times -= 1
            LOG.error(' %-20s ]-[ Get crash ids from server error. info: %s' % (LOG.get_function_name(), httperror.info()))
            if times != 0:
                time.sleep(2)
                self.get_task_list(version=version, date=new_date, times=times)
        except ReadFromServerException as read_err:
            raise ReadFromServerException(read_err.__str__())

    def get_crash_log(self, **args):
        """Get crash log from server.

        Arguments:
            task_id {String} -- [The crash id.]

        Returns:
            [Strint] -- [Crash contetn.]
        """
        LOG.debug(' %-20s ]-[ Get crash log with ID: %s' % (LOG.get_function_name(), args['task_id']))

        _req_l = list()

        header = {
            'ids': args['task_id'],
            'sign': self.get_md5(args['task_id'])
        }
        _req_l.append(request.Request(url=self.sc_get_log_url, headers=header, method='GET'))

        param = {
            'row': args['task_id']
        }
        parm_encode = parse.urlencode(param).encode('utf-8')
        _req_l.append(request.Request(url=self.wg_get_log_url, data=parm_encode, method='POST'))
        #LOG.info(_req_l)

        crash_content = bytes()

        for req_k, req_v in enumerate(_req_l):
            try:
                _request = None
                if args.__len__() > 1:
                    if args['projectname'] == 'WeGamers':
                        _request = request.urlopen(_req_l[-1])
                    elif args['projectname'] == 'GameLive':
                        _request = request.urlopen(_req_l[0])
                else:
                    _request = request.urlopen(req_v)
                if _request.getcode() == 200:
                    crash_content = _request.read()
                    #LOG.info(crash_content)
                    if crash_content.__len__() < 100:
                        crash_content = b''
            except request.HTTPError as HttpErr:
                LOG.debug(' %-20s ]-[ HTTPError with url %s, reason: %s, code: %s ' % (
                    LOG.get_function_name(),
                    HttpErr.geturl(),
                    HttpErr.reason,
                    HttpErr.code))
            except request.URLError as UrlErr:
                LOG.debug(' %-20s ]-[ UrlError with url %s, reason: %s' % (
                    LOG.get_function_name(),
                    req_v.get_full_url,
                    UrlErr.reason))
            finally: 
                if not crash_content:
                    if req_k == _req_l.__len__() - 1:
                        # if HttpErr:
                        #     raise ReadFromServerException("%s, %s" % (HttpErr.code, HttpErr.reason))
                        # elif UrlErr:
                        #     raise ReadFromServerException(UrlErr.reason)
                        # else:
                            #raise ReadFromServerException("can not read crash log with %s. Both WeGamers & StreamCraft." % args['task_id'])
                            crash_content = b''
                            return crash_content
                else:
                    LOG.debug(' %-20s ]-[ Get crash log with id(%s) done!' % (LOG.get_function_name(), args['task_id']))
                    LOG.info(crash_content)
                    return crash_content
 
    def get_task_log(self, version, que, date=YESTERDAY, platform='if'):
        """Generation each log via web API from analysis server.
        
        Arguments:
            version {String} -- [The spcified version]
        
        Keyword Arguments:
            date {String} -- [The date format string. E.g: 2018-03-17] (default: {YESTERDAY})
        
        Raises:
            ReadFromServerException -- [Getting nothing from server]
            TypeError -- [Maybe it is a useless raise.]

        Yield:
            [Tuple] -- (task_id, crash_log)
        """
        if isinstance(version, tuple):
            # Get crash ids from server
            task_ids = self.get_task_list(version=version, date=date, platform=platform)
            #LOG.info(task_ids)
            if not task_ids:
                que.put('Nothing has read.')
                raise ReadFromServerException('Getting nothing from server.')
            else:
                que.put('Crash from %s' % version[0])
                for index, task_id in enumerate(task_ids):
                    que.put('<h4>\t%d/%d Parsing...</h4>' % (index + 1, task_ids.__len__()))
                    _crash_log = self.get_crash_log(task_id=task_id, projectname=version[0])
                    yield task_id, _crash_log
        else:
            raise TypeError('The type error of variable "version". Expected %s. But %s ' % (type(tuple()), type(version)))

if __name__ == '__main__':
    crashinfo = GetCrashInfoFromServer()
    #crashinfo.get_task_list(('GameLive','V1.3.0 (4056)'), '2018-5-23', times=4, before=0)
    #crashinfo.get_crash_log(task_id='if-2009044592-1527012369681',projectname='GameLive')
    log = crashinfo.get_task_log(('GameLive','V1.8.1 (3312)'), que=queue.Queue(), date='2018-10-26', platform='af')
    for ln in log:
        LOG.info(ln[1])




