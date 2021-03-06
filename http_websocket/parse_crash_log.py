# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import os
import re

from . import sqlite_base
from . import subproc
from .init_dsym import DownloadDSYM
from .logger import Logger
from .parser_exception import ParseBaseInformationException, ParserException
from .similarity_compare import SimilarityCompute
from . import regular_common as search
import time

LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'ParseCrashLog')


class CrashParser:
    """Crash parsing class.
    
    Raises:
        ParserException -- Could not detected version information in this content.
        ParseBaseInformationException -- raw_data type unsupported!
        ParserException -- Can not detect product name from stacktrace content, this is an invalid log.
        ParserException -- The exception with ATOS command.
        ParseBaseInformationException -- Can't detect any product name from the crash log!
    
    Returns:
        Tuple -- 0)The maxmum line number of trackstack. 1)The start line.
        List  -- 0)version_number, 1)build_number, 2)app_use_for
        String -- Apple located reason.
        Tuple -- 0) Stacktrack log list. 1) CPU arch
        String -- The absolutely directory of the DSYM file.
        String -- The truthly crash reason after atos parsing.
        String -- The crash log after parse.
    """
    def __init__(self):
        super(CrashParser, self).__init__()
        self.build_number = str()
        self.version_number = str()
        self.proc = subproc.SubProcessBase()
        self.dsym = DownloadDSYM()

    def detect_maxtrac(self, crash_list):
        """Detect how much lines of the Stacktrace info.
        
        Arguments:
            crash_list {List} -- The list type of crash data.
        
        Returns:
            Tuple -- 1) max_line_number, 2) _id (Which line included the max line number, eg: -1, It is the negative index of list.)
        """
        _id = -1
        _pre_fix = int()
        if '_HOC' in crash_list.__str__():
            for _index, _start in enumerate(crash_list):
                if _start.startswith('Thread 0'):
                    _pre_fix = _index
                    break
        while True:
            try:
                _item = crash_list[_id]
                if _item.strip():
                    # try to set list[0] to a integer.
                    max_trac = int(_item.split()[0])
                    if _pre_fix:
                        return  len(crash_list) + _id - _pre_fix, _id
                    return max_trac + 1, _id
                else:
                    _id -= 1
            except ValueError:
                _id -= 1

    @staticmethod
    def get_ver_info(data_in):
        """Parsing version information from crash log

        Arguments:
            data_in {No limit} -- The crash log

        Raises:
            ParserException -- Could not detected version information in this content

        Returns:
            List -- 0)version_number, 1)build_number, 2)app_use_for
        """
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
            if 'version' in i or 'Version' in i:
                version_code = search.version_number(i)
                build_number = search.contsecutive_number(i)
                chinese = search.chinese(i)
                if hasattr(chinese, 'group'):
                    if search.chinese(i).group(0) == '正式版':
                        return [version_code.group(0), build_number.group(0), 'appstore']             #['1.3.0', '4056', 'appstore' ]
                else:
                    return [version_code.group(0), build_number.group(0), 'dev']
        raise ParserException('Could not detected version information in this content.')

    @staticmethod
    def get_apple_reason(raw_data):
        """Get apple located reason from log.

        Arguments:
            raw_data {String, Bytes} -- The crashes content.

        Returns:
            String -- Apple located reason.
        """
        content = list()
        if isinstance(raw_data, str):
            content = raw_data.split('\n')
        elif isinstance(raw_data, bytes):
            content = raw_data.decode().split('\n')
        for reason in content:
            if reason.startswith('reason:') or reason.startswith('ERROR:'):
                return reason
        LOG.error(' %-20s ]-[ This content is not included Apple Reason data.' % (LOG.get_function_name()))

    def get_stacktrack_list(self, crash_list, project_name):
        """Filter all the Stacktrack log from log content.

        Arguments:
            crash_list {List} -- List type log.
            pro_name {String} -- The name of project.

        Returns:
            Tuple -- 0) Stacktrack log list. 1) CPU arch
        """
        nstacktrace_max, _id = self.detect_maxtrac(crash_list=crash_list)
        stacktrace_list = list()
        for i in range(nstacktrace_max):
            # Get negative index number of this line.
            _index = _id - i
            line = crash_list[_index].split()
            # Get list data by reverse order.
            for x in line:
                # Special handle for StreamCraft.
                if project_name in x or 'StreamCraft' in x:
                    # Get memory start adress
                    _memory_addr_start = hex(
                        int('%s' % line[2], 16) - int(line[-1]))        #转成16进制
                    # Get memory stack adress
                    _memory_addr_stack = line[2]
                    # Merge mulitple data to list.
                    less_line = [_index, line[0], line[1],
                                _memory_addr_stack, _memory_addr_start, line[-1]]
                    stacktrace_list.append(less_line)
                    break
        if stacktrace_list:
            # Detect stack memory address length. >10 is 64bit.
            if len(stacktrace_list[-1][3]) == 10:
                return stacktrace_list, 'armv7'
            else:
                return stacktrace_list, 'arm64'
        else:
            return 0, 0

    def get_dsym_file(self, parent_dir, product_name):
        """Get the DSYM absolutely directory
        
        Arguments:
            parent_dir {String} -- The parent directory to save the DSYM file.
            product_name {String} -- The product name to locate.
        
        Returns:
            String -- The absolutely directory of the DSYM file.
        """
        for dir_items in os.walk(parent_dir):
            # dir_items[0] = absolutely parent directory.
            # dir_items[1] = the child directory in the current directory.
            # dir_items[2] = the files list of the current directory.
            for _file in dir_items[-1]:
                # Special handle for StreamCraft.
                if product_name in _file or 'StreamCraft' in _file:
                    return os.path.join(dir_items[0], _file)

    def atos_run(self, dSYM_file, tableid, version, crash_id, raw_data, product_name):
        """ATOS command entrance.
        
        Arguments:
            dSYM_file {String} -- The DSYM file absolute dir.
            tableid {Integer} -- The crash log location in the table statistics.
            crash_id {String} -- The crash log ID.
            raw_data {String} -- The crash log content.
            product_name {String} -- The product name of the crash log.
        
        Raises:
            ParseBaseInformationException -- raw_data type unsupported!
            ParserException -- Can not detect product name from stacktrace content, this is an invalid log.
            ParserException -- The exception with ATOS command.
        
        Returns:
            String -- The truthly crash reason after atos parsing.
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
        _app_symbol_file = self.get_dsym_file(dSYM_file, product_name)

        time.sleep(3)
        for dir in os.listdir(os.path.join(dSYM_file, 'Contents', 'Resources', 'DWARF')):
            if 'SC' in dir:
                os.rename(os.path.join(dSYM_file, 'Contents', 'Resources', 'DWARF', dir),
                          os.path.join(dSYM_file, 'Contents', 'Resources', 'DWARF', 'StreamCraft'))

        # call get_crash_list to filter what data need to parsing.
        stacktrace_list, cpu_arm_ = self.get_stacktrack_list(crash_list=crash_list, project_name=product_name)       #[_index, line[0], line[1],memory_addr_stack, _memory_addr_start, line[-1]],'arm64'

        if not stacktrace_list:
            # Useless crash log.
            conn, cursor = sqlite_base.sqlite_connect()
            sqlite_base.insert(conn, cursor,
                               table_name='unmatch',
                               crash_id=crash_id)
            raise ParserException('Can not detect product name from stacktrace content, this is an invalid log.')

        for _index, _value in enumerate(stacktrace_list):            #[ [_index, line[0], line[1],_memory_addr_stack, _memory_addr_start, line[-1]],[...] ]

            # Pick memory address
            _line_id = _value[0]
            _stacktrac_id = _value[1]
            _produce_name_raw = _value[2]
            _memory_addr = _value[3]
            _base_addr = _value[4]
            _offset = _value[-1]

            # Splicing ATOS command.
            atos_cmd = ' '.join([
                atos, arch, cpu_arm_, op, _app_symbol_file,                  #解压后，目录下的StreamCraft文件
                _l, _base_addr, _memory_addr])

            # Call subprocess to run atos command.
            try:
                parse_result = self.proc.sub_procs_run(cmd=atos_cmd)
                if parse_result:
                    result = parse_result.stdout.decode().replace('\n', '')
                    # Append result to result list.
                    _l_method_call.append(result)
            except Exception as atos_err:
                raise ParserException(atos_err.__str__())

            # Splicing data what need to replace.
            replace_data = '   '.join([
                _stacktrac_id, _produce_name_raw, _memory_addr, _offset, result])
            # Replace raw data, and the tabs add or not.
            if '\t' in crash_list[_line_id]:
                crash_list[_line_id] = '\t' + replace_data
            else:
                crash_list[_line_id] = replace_data

        # Insert the crash information to sql.
        if tableid:
            conn, cursor = sqlite_base.sqlite_connect()
            # Insert the truthly crash reasons.
            # For compute frenquency of appearing.
            sqlite_base.update(conn, cursor,
                               table_name='backtrack_%d' % tableid,
                               reason=','.join(_l_method_call),                    #reason
                               condition="where CRASH_ID = '%s'" % crash_id,
                               end=False)
            # Insert the final crash log to table report.
            # Use for submit to JIRA.
            sqlite_base.insert(conn, cursor,
                               table_name='report',
                               crash_id=crash_id,
                               project=product_name,
                               version=version,
                               crash_call=_l_method_call[-1],
                               log='\n'.join(crash_list))
        # List to String.
        return '\n'.join(crash_list)

    def parsing(self, raw_data, project_list, version_info=0, product_name=0, task_id=0):
        """Parsing come in log data.

        Arguments:
            raw_data {String, Bytes} -- [This is from webpage or input. No limited type on there.]
            project_list {[List]} -- [All the list include project from JIRA.]

        Keyword Arguments:
            version_info {String} -- [Version type. 1)appstore 2)dev] (default: {0})
            product_name {String} -- [Product name of this log.] (default: {0})
            task_id {String} -- [This is the id of this log when it from web.] (default: {0})

        Raises:
            ParseBaseInformationException -- Can't detect any product name from the crash log!

        Returns:
            String -- The crash log after parse.
        """

        _row_id = int()
        # Set value to _product_name when product name has detected.
        if not product_name:
            _raw_data = str()
            if isinstance(raw_data, bytes):
                _raw_data = raw_data.decode()
            else:
                _raw_data = raw_data
            for _name in project_list.values():
                if 'StreamCraft' in _raw_data or 'SC' in _raw_data:                #2018.11.6
                    product_name = 'STREAMCRAFT'
                elif _name in _raw_data:
                    product_name = _name
                print (product_name)
                break
            if not product_name:
                raise ParseBaseInformationException('Can\'t detect any product name from the crash log!')

        # Get version info from raw data.
        if not version_info:
            version_info = CrashParser.get_ver_info(raw_data)         # #['1.3.0', '4056', 'appstore' ]

        # Download dSYM file if not exists.
        abs_dsym = self.dsym.init_dsym(version_number=version_info[0],
                                       build_id=version_info[1],
                                       version_type=version_info[-1],
                                       product_name=product_name,
                                       product_list=project_list)

        # Get apple reason.
        _reason = CrashParser.get_apple_reason(raw_data=raw_data)

        # Compute similarity with old data.
        if task_id:
            _sc = SimilarityCompute(project=product_name, versioninfo=version_info[0], crashid=task_id)
            _row_id = _sc.apple_locate_similarity(_reason)

        # Parse Stacktrace information.
        return self.atos_run(dSYM_file=abs_dsym,
                             version=version_info[0],
                             product_name=product_name,
                             raw_data=raw_data,
                             tableid=_row_id,
                             crash_id=task_id)
