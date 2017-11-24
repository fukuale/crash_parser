# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import re

import os
from urllib import parse, request

from http_websocket.similarity_compare import SimilarityCompute

try:
    from logger import Logger
    from init_dsym import DownloadDSYM
    from parser_exception import ParserException
    import subproc
    import sqlite_base
except ModuleNotFoundError as e:
    from http_websocket.logger import Logger
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.parser_exception import ParserException, ParseBaseInformationException
    import http_websocket.subproc as subproc
    import http_websocket.sqlite_base as sqlite_base

log_file = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
log = Logger(log_file, 'ParseCrashLog')


class CrashParser:
    def __init__(self):
        super(CrashParser, self).__init__()
        self.report_sql = 'ReportInfo.sqlite'
        self.build_number = str()
        self.version_number = str()
        self.proc = subproc.SubProcessBase()
        self.dSYM = DownloadDSYM()

    def detect_maxtrac(self, crash_list):
        """
        Detect how much lines of the Stacktrace info.
        :return: Tuple object.
            1) max_line_number
            2) _id (Which line included the max line number, eg: -1, It is the negative index of list.)
        """

        _id = -1
        while True:
            try:
                # try to set list[0] to a integer.
                max_trac = int(crash_list[_id].split()[0])
                return max_trac + 1, _id
            except ValueError:
                _id -= 1

    @staticmethod
    def get_ver_info(data_in):
        """
        Get application information from crash log.
        :return: Tuple object.
            1)version code
            2)build number
            3)version type
        """
        # Complier regular expression
        _version = re.compile(r'\d+(\.\d+){0,2}')  # version code
        _build = re.compile(r'[\d]+')  # Consecutive numbers (for build number)
        _ver_type = re.compile(r'[\u4e00-\u9fa5]+')  # Match chinese (for version type)

        # Change data type to list object.
        content = list()
        if isinstance(data_in, bytes):
            content = data_in.decode().split('\n')
        elif isinstance(data_in, str):
            content = data_in.split('\n')
        elif isinstance(data_in, list):
            content = data_in

        # Parsing version info
        for i in content:
            if 'version' in i:
                version_code = _version.search(i)
                build_number = _build.findall(i)
                if _ver_type.findall(i)[0] == '正式版':
                    return [version_code.group(0), build_number[-1], 'appstore']
                else:
                    return [version_code.group(0), build_number[-1], 'dev']
        raise ParserException('Could not detected version information.')

    @staticmethod
    def get_apple_reason(raw_data):
        """
        Get "apple reason" feedback from crash log.
        This data is used to store data in each data table first time. [Data table split]
        :return: String object
        """
        content = list()
        if isinstance(raw_data, str):
            content = raw_data.split('\n')
        elif isinstance(raw_data, bytes):
            content = raw_data.decode().split('\n')
        for reason in content:
            if reason.startswith('reason:') or reason.startswith('ERROR:'):
                return reason
        log.error(' %-20s ]-[ This content is not included Apple Reason data.' % (log.get_function_name()))

    def get_crash_list(self, crash_list, pro_name):
        """
        Get each line included product_name from Stacktrace content.
        :return: Tuple object
            1)List object. The stacktrace_list
            2)String object. CPU Arch type.
        """
        nstacktrace_max, _id = self.detect_maxtrac(crash_list=crash_list)
        stacktrace_list = list()
        for i in range(nstacktrace_max):
            # Get negative index number of this line.
            _index = _id - i
            line = crash_list[_index].split()
            # Get list data by reverse order.
            if pro_name in line:
                # Get memory start adress
                _memory_addr_start = hex(
                    int('%s' % line[2], 16) - int(line[-1]))
                # Get memory stack adress
                _memory_addr_stack = line[2]
                # Merge mulitple data to list.
                less_line = [_index, line[0], line[1],
                             _memory_addr_stack, _memory_addr_start, line[-1]]
                stacktrace_list.append(less_line)
        if stacktrace_list:
            # Detect stack memory address length. >10 is 64bit.
            if len(stacktrace_list[-1][3]) == 10:
                return stacktrace_list, 'armv7'
            else:
                return stacktrace_list, 'arm64'
        else:
            return 0, 0

    def atos_run(self, dSYM_file, tableid, crash_id, raw_data, product_name):
        """
        Run all method to parsing crash info to get parameters to run atos.
        Run atos command to parsing method call from symbol package.
        :param dSYM_file: dSYM file absolute folder address.
        :return: String object
        """
        crash_list = list()
        if isinstance(raw_data, bytes):
            crash_list = raw_data.decode().split('\n')
        elif isinstance(raw_data, str):
            crash_list = raw_data.split('\n')
        else:
            raise ParseBaseInformationException('raw_data type unsupported!')

        # Splicing the dSYM absolute location to get the application binary absolute location on dSYM file.
        atos = 'atos'
        arch = '-arch'
        op = '-o'
        _l = '-l'
        _l_method_call = list()
        _app_symbol_file = dSYM_file + '/Contents/Resources/DWARF/%s' % product_name

        # call get_crash_list to filter what data need to parsing.
        stacktrace_list, cpu_arm_ = self.get_crash_list(crash_list=crash_list, pro_name=product_name)

        if not stacktrace_list:
            conn, cursor = sqlite_base.sqlite_connect()
            sqlite_base.insert(conn, cursor,
                               table_name='unmatch',
                               crash_id=crash_id)
            raise ParserException('Can not detect product name from stacktrace content, this is a invalid log.')
        # enumerate wait to parsing data
        for _index, _value in enumerate(stacktrace_list):

            # Pick memory address
            line_id = _value[0]
            stacktrac_id = _value[1]
            produce_name_raw = _value[2]
            memory_addr = _value[3]
            base_addr = _value[4]
            offset = _value[-1]
            # Parsing stack address to get the truth crash method.
            # Splicing atos command.
            atos_cmd = ' '.join([
                atos, arch, cpu_arm_, op, _app_symbol_file,
                _l, base_addr, memory_addr])
            # Call subprocess to run atos command.
            parse_result = self.proc.sub_procs_run(cmd=atos_cmd)
            if parse_result:
                result = parse_result.stdout.decode().replace('\n', '')
                # Append result to result list.
                _l_method_call.append(result)
            else:
                raise ParserException('Atos error')
            # Splicing data what need to replace.
            replace_data = '   '.join([
                stacktrac_id, produce_name_raw, memory_addr, offset, result])
            # Replace data, and the tabs add or not.
            if '\t' in crash_list[line_id]:
                crash_list[line_id] = '\t' + replace_data
            else:
                crash_list[line_id] = replace_data
        # Insert to sql the crash information.
        if tableid:
            conn, cursor = sqlite_base.sqlite_connect()
            # Insert crash method call.
            # Used to compute frenquency of appearing.
            sqlite_base.update(conn, cursor,
                               table_name='backtrack_%d' % tableid,
                               reason=','.join(_l_method_call),
                               condition="where CRASH_ID = '%s'" % crash_id)
            # Insert the final crash log after parsing to table report.
            # Used to submit to JIRA.
            conn_db2, cursor_db2 = sqlite_base.sqlite_connect(self.report_sql)
            sqlite_base.insert(conn_db2, cursor_db2,
                               table_name='report',
                               crash_id=crash_id,
                               log='\n'.join(crash_list))
        return '\n'.join(crash_list)

    def parsing(self, raw_data, conf_files, product_name=0, task_id=0):
        """
        Parsing
        :param conf_files:
        :param raw_data:
        :param product_name:
        :param task_id:
        :return:
        """
        # Set value to _product_name when product name was detected.
        if not product_name:
            _raw_data = str()
            if isinstance(raw_data, bytes):
                _raw_data = raw_data.decode()
            else:
                _raw_data = raw_data
            for names in conf_files:
                if os.path.splitext(names)[0] in _raw_data:
                    product_name = os.path.splitext(names)[0]
                    if '_HOC' in _raw_data:
                        product_name += '_HOC'
                    break
            if not product_name:
                raise ParseBaseInformationException('Can\'t detect any product name from the crash log!')

        # Get version info from raw data.
        _version_info = CrashParser.get_ver_info(raw_data)

        # Download dSYM file if not exists.
        abs_dsym = self.dSYM.init_dSYM(version_number=_version_info[0],
                                       build_id=_version_info[1],
                                       version_type=_version_info[-1],
                                       product=product_name)

        # Get apple reason.
        _reason = CrashParser.get_apple_reason(raw_data=raw_data)

        # Compute similarity with old data.
        _sc = SimilarityCompute(versioninfo=_version_info[0], crashid=task_id)
        _row_id = _sc.apple_locate_similarity(_reason)

        # Parse Stacktrace information.
        return self.atos_run(dSYM_file=abs_dsym,
                             product_name=product_name,
                             raw_data=raw_data,
                             tableid=_row_id,
                             crash_id=task_id)
