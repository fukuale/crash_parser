# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import os
from multiprocessing import Manager, Pool, Queue

import zmq

import regular_common
from get_crash_log import GetCrashInfoFromServer
from init_dsym import DownloadDSYM
from jira_handler import JIRAHandler
from logger import Logger
from parse_crash_log import CrashParser
from parser_exception import (BreakProcessing, ParseBaseInformationException,
                              ReadFromServerException)
from read_build_ftp import ReadVersionInfoFromFTP
from report_export import ReportGenerator

LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'TaskManager')

class TaskSchedule(object):
    """Scheduling.
    """
    def __init__(self):
        super(TaskSchedule, self).__init__()

        # Truth project name
        self.pjname = {
            'GAMEIM': 'WeGamers',
            'WELIVE': 'GameLive'
            }

        # Get configuration file, product name.
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'conf')

        # Get all the configuration files under [CrashParser] path, except invalid configuration files.
        # os.walk to read all files name under target path.
        # loop this files name list.
        # filter data to append list.
        self.conf_files = [z for a, b, x in os.walk(self.conf_dir) for z in x if
                           not z.startswith('_') and not z.startswith('.')]

        # Variable type define
        self.crash_info_env = list()
        self.current_app_name = int()
        self.dsym_abspath = str()
        self.parser_wait_raw = str()

        # Instance base class.
        self.get_log = GetCrashInfoFromServer()
        self.dsym = DownloadDSYM()
        self.parser = CrashParser()

        # JIRA Handler
        self.jira = JIRAHandler()

        # Read build svn code
        self.build_code = ReadVersionInfoFromFTP()

    def gen_version_list(self):
        """Read versions info from JIRA server.

        Raises:
            ParseBaseInformationException -- [description]

        Yields:
            [Tuple] -- 0)Product name, 1)Version info of this project.EG. V1.1.1XXX
        """
        for proj in self.jira.get_projects():
            if proj[0] in self.pjname.keys():
                # Read newest 5 versions from JIRA
                _ver_l = self.jira.read_project_versions(project_name=proj[0])
                # Stitching version information to read crash ids from server
                if _ver_l.__len__() > 0:
                    _version_s = self.build_code.stitching_last_version(project_name=proj[0], jira_ver=_ver_l)
                    if _version_s:
                        yield self.pjname[proj[0]], _version_s
                    else:
                        LOG.error(' %-20s ]-[ Can not detected svn code with project name(%s) and versions{%s} from build server!' % (LOG.get_function_name(), proj[0], _ver_l))
                        raise ParseBaseInformationException("Can not detected svn code with project name(%s) and versions{%s} from build server!" % (proj[0], _ver_l))
                else:
                    raise ParseBaseInformationException("Can not read version with project(%s)" % proj[0])

    def read_log_from_server(self):
        """Getting each crash log from server.
        
        Raises:
            ReadFromServerException -- [getting nothing from server]

        Yield:
            [Tuple] -- ((Crash id, Crash log), (project name, version information))
        """
        _version_l = self.gen_version_list()
        _no_log_l = list()
        count = 0
        for version in _version_l:
            # Read log with version information.
            count += 1
            try:
                _c_log = self.get_log.get_task_log(version=version)
                for _log in _c_log:
                    if version[0] == 'GameLive':
                        # Special handle for StreamCraft.
                        if 'StreamCraft' in _log[-1].decode():
                            yield _log, version
                    elif version[0] in _log[-1].decode():
                        yield _log, version
            except ReadFromServerException:
                _no_log_l.append(version)
        if _no_log_l.__len__() == count:
            raise ReadFromServerException("No crash can be read with this version{%s}" % str(_no_log_l))


    # TODO: MULTIPLE PROCESS SUPPORT !
    def run_parser(self, raw_data=None):
        """Parser logic.

        Keyword Arguments:
            raw_data {String} -- [Crahes content.] (default: {None})
            queue_in {[} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """
        # Url or crash id in.
        
        if raw_data != 'guopengzhang':
            #Url in.
            if raw_data.startswith('http'):
                _regular_result = regular_common.crash_id(raw_data)
                if hasattr(_regular_result, 'group'):
                    task_id = _regular_result.group(0)
                else:
                    return 'Incomplete Link. Please paste that what link you can get crash information on browser!'
            # Crash id in.
            elif raw_data.startswith('if'):
                task_id = raw_data

                crash_content = self.get_log.get_crash_log(task_id=task_id)
                if len(crash_content) > 100:
                    return self.parser.parsing(raw_data=crash_content,
                                            project_list=self.pjname)
                else:
                    return "Can\'t read any content from the link. \nCheck it manully !"
            # Crash log in.
            elif ("deviceType" in raw_data and "0x00" in raw_data and "version" in raw_data) or (
                     "Hardware Model" in raw_data and "Version" in raw_data):
                return self.parser.parsing(raw_data=raw_data,
                                            project_list=self.pjname)
            else:
                return 'Can\'t read environment information from this log content. ' \
                    '\nCheck it manually !\n\n Do not fool me  _(:3 」∠)_'
            # Exculd empty page
        # Crash content in.
        elif 'version' in raw_data:
            return self.parser.parsing(raw_data=raw_data,
                                       project_list=self.pjname.values())
        # Automatic parsing.
        elif raw_data == 'guopengzhang':
            try:
                for crash_info in self.read_log_from_server():
                    _project_name = str()
                    env = self.parser.get_ver_info(crash_info[0][-1])
                    # TODO: CONTINUE FROM HERE.
                    for key, _proj_name in enumerate(self.pjname.values()):
                        _log = str(crash_info[0][-1])
                        # Special handle for StreamCraft.
                        if _proj_name in _log or 'StreamCraft' in _log:
                            _project_name = _proj_name
                            break
                        else:
                            if key == self.pjname.values().__len__() - 1:
                                raise BreakProcessing('Can not detected the valid project name from this content.')

                    abs_dsym = self.dsym.init_dsym(version_number=env[0],
                                                   build_id=env[1],
                                                   version_type=env[-1],
                                                   product_name=crash_info[-1][0],
                                                   product_list=self.pjname)
                    if abs_dsym:
                        self.parser.parsing(raw_data=crash_info[0][-1],
                                            product_name=crash_info[-1][0],
                                            version_info=env,
                                            task_id=crash_info[0][0],
                                            project_list=self.pjname.values())
                # TODO: PROGRESSING
                self.jira_handler()
            except Exception as e:
                return e

    def jira_handler(self):
        """Call JIRA method.
        """
        _report_gen = ReportGenerator(product_name_list=self.pjname.values())
        _report_gen.submit_jira(pjname_dict=self.pjname)
        _report_gen.update_jira()

    def start(self):
        """[summary]
        """
        # Start ZMQ socket server
        context = zmq.Context.instance()
        socket = context.socket(zmq.REP)
        socket.connect("tcp://127.0.0.1:7725")
        # Listen to receive.
        task_content = socket.recv()
        # Bytes to String.
        if hasattr(task_content, "decode"):
            task_content = task_content.strip().decode()
        try:
            result = self.run_parser(task_content)
            if result:
                socket.send_string(str(result))
            else:
                socket.send_string("Finish")
        except Exception as parser_err:
            socket.send_string(parser_err.__str__())        

if __name__ == '__main__':
    ts = TaskSchedule()
    while 1:
        ts.start()
