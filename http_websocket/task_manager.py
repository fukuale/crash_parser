# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import os

# Cause IDE need parent folder name to import other class, shell need not.
try:
    from parser_exception import ParseBaseInformationException
    from similarity_compare import SimilarityCompute
    from get_crash_log import GetCrashInfoFromServer
    from parse_crash_log import CrashParser
    from init_dsym import DownloadDSYM
    from subproc import SubProcessBase
    from jira_handler import JIRAHandler
    from report_export import ReportGenerator
    from read_build_ftp import ReadVersionInfoFromFTP
except ModuleNotFoundError:
    from http_websocket.parser_exception import ParseBaseInformationException
    from http_websocket.similarity_compare import SimilarityCompute
    from http_websocket.get_crash_log import GetCrashInfoFromServer
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.subproc import SubProcessBase
    from http_websocket.jira_handler import JIRAHandler
    from http_websocket.report_export import ReportGenerator
    from http_websocket.read_build_ftp import ReadVersionInfoFromFTP


class TaskSchedule(object):
    def __init__(self):
        super(TaskSchedule, self).__init__()
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
        self.dSYM_abspath = str()
        self.parser_wait_raw = str()

        # Instance base class.
        self.get_log = GetCrashInfoFromServer()
        self.dSYM = DownloadDSYM()
        self.parser = CrashParser()

        # JIRA Handler
        self.jira = JIRAHandler()

        # Read build svn code
        self.build_code = ReadVersionInfoFromFTP()

        # Truth project name
        self.pjname = {'GAMEIM': 'WeGamers',
                       'WELIVE': 'StreamCraft'}

    def gen_version_list(self):
        """
        Read version info from JIRA server.
        :return:
            0) self.pjname[proj]: The truth project name with crash log.
            1) _code_l: The last 3 version information of project.
        """
        for proj in self.jira.get_projects():
            if proj:
                # Read last 3 versions of this project from JIRA.
                _ver_l = self.jira.read_project_versions(project=proj[0])
                # Splicing version information for read crash ids from server.
                _version_s = self.build_code.read_last_svn_code(project=proj[0], jira_ver=_ver_l)
                if _version_s:
                    yield self.pjname[proj[0]], _version_s
                else:
                    raise ParseBaseInformationException('Can not detected version [Project:%s] from build server!' % proj)

    def read_log_from_server(self):
        """
        Interpreter generator to get crash log from server.
        Generation tuple data.
        :return:
            0) _log[0]: The id of crash log.
            1) _log[1]: The crash log content.
            2) version[0]: The project name.
        """
        for version in self.gen_version_list():
            # Read log with version information.
            _c_log = self.get_log.gen_task_log(version=version[-1])
            for _log in _c_log:
                if version[0] in _log[-1].decode():
                    yield _log, version

    # TODO MULTIPLE PROCESS SUPPORT !
    def run_parser(self, raw_data=None, queue_in=None):
        if raw_data.startswith('http') or raw_data.startswith('if'):
            task_id = str()
            if raw_data.startswith('http'):
                if raw_data.find('row=') >= 0:
                    task_id = raw_data.split('=')[-1]
                else:
                    return 'Incomplete Link. Please paste that what link you can see crash information on browser!'

            elif raw_data.startswith('if'):
                task_id = raw_data

            crash_content = self.get_log.get_crash_log(task_id=task_id)
            if len(crash_content) > 100:
                return self.parser.parsing(raw_data=crash_content,
                                           project_list=self.pjname.values())
            else:
                return 'Can\'t read any content from the link. \nCheck it manully !'
        elif 'version' in raw_data:
            return self.parser.parsing(raw_data=raw_data,
                                       project_list=self.pjname.values())
        # TODO: START AT HERE.
        elif 'guopengzhang' == raw_data:
            try:
                for crash_info in self.read_log_from_server():
                    env = self.parser.get_ver_info(crash_info[-1][-1])
                    # TODO: PROCESSING.
                    abs_dsym = self.dSYM.init_dSYM(version_number=env[0],
                                                   build_id=env[1],
                                                   version_type=env[-1],
                                                   product=crash_info[-1][0])
                    if abs_dsym:
                        self.parser.parsing(raw_data=crash_info[0][-1],
                                            product_name=crash_info[-1][0],
                                            task_id=crash_info[0][0],
                                            project_list=self.pjname.values())
            except Exception as e:
                return e.__str__()

        else:
            return 'Can\'t read environment information from this log content. ' \
                   '\nCheck it manually !\n\n Do not fool me  _(:3 」∠)_'

    def jira(self):
        rg = ReportGenerator(product_name_list=self.pjname.values())
        rg.submit_jira()
        rg.update_jira()
