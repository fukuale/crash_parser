# Author = 'Vincent FUNG'
# Create = '2017/09/24'

import hashlib
from urllib import parse
from urllib import request
import datetime
import time
import queue

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
        """Compute sign key to access crash log API

        Arguments:
            date {String} -- [Date timestamp.]

        Returns:
            [String] -- [The MD5 of date.]
        """
        md5 = hashlib.md5()
        md5.update((self.sec_key + str(date)).encode())
        return md5.hexdigest().lower()

    def get_task_list(self, version, date):
        """Get crash_id from web API

        Arguments:
            version {String} -- [The version from JIRA]
            date {String} -- [Date timestamp.]

        Returns:
            [List] -- [The crash ids list.]
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
            LOG.info(' %-20s ]-[ Crash id list from server: \n%s' % (LOG.get_function_name(), str(task_list)))
            # Validation data validity.
            if len(task_list) > 10:
                # Source data transition to list type.
                return eval(task_list)
        # Retry for HTTP 404 temporary
        except request.HTTPError as httperror:
            times -= 1
            LOG.error(' %-20s ]-[ Get crash ids from server error. info: %s' % (LOG.get_function_name(), httperror.info()))
            if times != 0:
                time.sleep(2)
                self.get_task_list(version, date)
        # TODO: Add Exception to comleting this logic.

    def get_crash_log(self, task_id):
        """Get crash log from server.

        Arguments:
            task_id {String} -- [The crash id.]

        Returns:
            [Strint] -- [Crash contetn.]
        """
        LOG.debug(' %-20s ]-[ Get crash log with ID: %s' % (LOG.get_function_name(), task_id))
        param = {'row': task_id}

        parm_encode = parse.urlencode(param).encode('utf-8')

        crash_page = request.Request(
            url=self.read_ids_url,
            data=parm_encode
        )

        crash_content = request.urlopen(crash_page).read()
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
        if isinstance(version, str):
            # Get crashes
            task_ids = self.get_task_list(version=version, date=date)
            if not task_ids:
                raise ReadFromServerException('No content has read.')
            else:
                for task_id in task_ids:
                    _crash_log = self.get_crash_log(task_id)
                    yield task_id, _crash_log
        else:
            raise TypeError('The type error of variable "version". Expected %s. But %s ' % (type(str()), type(version)))
