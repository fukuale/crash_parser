# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import hashlib
from urllib import parse
from urllib import request
import datetime
import time
import queue
import sys
import os

# try:
from logger import Logger
from subproc import SubProcessBase
from parser_exception import ReadFromServerException
# except ModuleNotFoundError as e:
#     from http_websocket.logger import Logger
#     from http_websocket.subproc import SubProcessBase
#     from http_websocket.parse_crash_log import CrashParser
#     from http_websocket.parser_exception import ReadFromServerException

LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
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
        # self.sc_domain = 'http://crec.streamcraft.com:95'
        self.sc_domain = 'http://10.0.21.75:8181'
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

    def get_task_list(self, version, date, times=4, before=0):
        """Get crash_id from web API

        Arguments:
            version {String} -- [The version from JIRA]
            date {String} -- [Date timestamp.]

        Returns:
            [List] -- [The crash ids list.]
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

            _req = request.Request(url=self.wg_get_ids_url, data=url_params, method='POST')

        # Set request parameters to headers and request via method GET.
        elif version[0] == 'StreamCraft':
            # Change the date format to %Y%m%d from %Y-%m-%d
            _strpdate = datetime.datetime.strftime(
                datetime.datetime.strptime(date, '%Y-%m-%d'),
                '%Y%m%d'
            )
            # Headers set.
            header = {
                'date': _strpdate,
                'sign': self.get_md5(_strpdate)
            }

            _req = request.Request(url=self.sc_get_ids_url, headers=header, method='GET')
        else:
            raise ReadFromServerException("Projectname match no options. Can not read crash ids list.")
        try:
            # TODO: Http status 200 judge logic. to ensure the server still works.
            task_list = request.urlopen(_req).read()
            # Validation data validity.

            # validation the first character is symbol "[". If it's, that could eval to list. if not, that result is useless.
            if task_list[0] == 91:
                _task_list = eval(task_list)
                # remove the id is not startswith 'if'. if=iOS Crash.
                _temp_list = list()
                for x in _task_list:
                    if not x.startswith('i'):
                        _temp_list.append(x)
                _task_list = list(set(_task_list).difference(_temp_list))
                # If len == 0. Try to get the the day before.
                if _task_list.__len__() != 0:
                    return _task_list
                elif _task_list.__len__() == 0 and not before:
                    before += 1
                    LOG.info(' %-20s ]-[ Crash id list from server: \n%s' % (LOG.get_function_name(), [_req.full_url, _req.data, _req.headers]))
                    new_date = str((datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(1)).date())
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

    def get_crash_log(self, task_id, projectname):
        """Get crash log from server.

        Arguments:
            task_id {String} -- [The crash id.]

        Returns:
            [Strint] -- [Crash contetn.]
        """
        LOG.debug(' %-20s ]-[ Get crash log with ID: %s' % (LOG.get_function_name(), task_id))

        _req = request.Request

        if projectname == 'WeGamers':
            param = {
                'row': task_id
            }

            parm_encode = parse.urlencode(param).encode('utf-8')

            _req = request.Request(url=self.wg_get_log_url, data=parm_encode, method='POST')
        elif projectname == 'StreamCraft':
            header = {
                'ids': task_id,
                'sign': self.get_md5(task_id)
            }

            _req = request.Request(url=self.sc_get_log_url, headers=header, method='GET')
        else:
            raise ReadFromServerException("Projectname match no options. Can not get crash infomation.")
        # TODO: Http status 200 judge logic. to ensure the server still works.
        crash_content = request.urlopen(_req).read()
        LOG.debug(' %-20s ]-[ Get crash log with id(%s) done!' % (LOG.get_function_name(), task_id))
        return crash_content

    def get_task_log(self, version, date=YESTERDAY):
        """Get the log content from web API within specific id.
        
        Arguments:
            version {[type]} -- [description]
        
        Keyword Arguments:
            date {[type]} -- [description] (default: {YESTERDAY})
        
        Raises:
            ReadFromServerException -- [description]
            TypeError -- [description]
        
        Yields:
            [type] -- [description]
        """
        if isinstance(version, tuple):
            # Get crashes
            task_ids = self.get_task_list(version=version, date=date)
            if not task_ids:
                raise ReadFromServerException('No content has read.')
            else:
                for task_id in task_ids:
                    _crash_log = self.get_crash_log(task_id, version[0])
                    yield task_id, _crash_log
        else:
            raise TypeError('The type error of variable "version". Expected %s. But %s ' % (type(tuple()), type(version)))
