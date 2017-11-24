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
    from report_export import ReportGenerator
except ModuleNotFoundError:
    from http_websocket.parser_exception import ParseBaseInformationException
    from http_websocket.similarity_compare import SimilarityCompute
    from http_websocket.get_crash_log import GetCrashInfoFromServer
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.subproc import SubProcessBase
    from http_websocket.report_export import ReportGenerator


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

    def gen_version_list(self):
        """
        Parsing configuration files on path "~/CrashParser/conf/".
        Get what version need to parsing.
        Generation tuple data.
        :return:
            0) vn.strip() : str(version_name), like: v1.9.5 (11311) appstore.
            1) os.path.splitext(v)[0] : str(product_name)
        """
        for k, v in enumerate(self.conf_files):
            _v_list = open(os.path.join(self.conf_dir, v), 'r', encoding='utf-8').readlines()
            for vn in _v_list:
                if vn:
                    yield vn.strip()

    # Get the crash log generator
    def read_log_from_server(self):
        """
        Interpreter generator to get crash log from server.
        Generation tuple data.
        :return:
            0) _c_log : crash log get generator.
            1) version[1] : this is str(product_name)
        """
        for version in self.gen_version_list():
            _c_log = self.get_log.gen_task_log(version=version)
            for _log in _c_log:
                for names in self.conf_files:
                    if os.path.splitext(names)[0] in _log[-1].decode():
                        _product_name = os.path.splitext(names)[0]
                        yield _log[0], _log[1], _product_name

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
                                           conf_files=self.conf_files)
            else:
                return 'Can\'t read any content from the link. \nCheck it manully !'
        elif 'version' in raw_data:
            return self.parser.parsing(raw_data=raw_data,
                                       conf_files=self.conf_files)
        elif 'guopengzhang' == raw_data:
            for crash_info in self.read_log_from_server():
                env = self.parser.get_ver_info(crash_info[1])
                abs_dsym = self.dSYM.init_dSYM(version_number=env[0],
                                               build_id=env[1],
                                               version_type=env[-1],
                                               product=crash_info[-1])
                if abs_dsym:
                    self.parser.parsing(raw_data=crash_info[1],
                                        product_name=crash_info[-1],
                                        task_id=crash_info[0],
                                        conf_files=self.conf_files)
            self.jira()
        else:
            return 'Can\'t read environment information from this log content. ' \
                   '\nCheck it manually !\n\n Do not fool me  _(:3 」∠)_'

    def jira(self):
        _project_name_l = [os.path.splitext(x)[0] for x in self.conf_files]
        rg = ReportGenerator(product_name_list=_project_name_l)
        rg.submit_jira()
        rg.update_jira()
