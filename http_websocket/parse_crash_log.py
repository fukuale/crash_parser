# Author = 'Vincent FUNG'
# Create = '2017/09/20'
#                       ::
#                      :;J7, :,                        ::;7:
#                      ,ivYi, ,                       ;LLLFS:
#                      :iv7Yi                       :7ri;j5PL
#                     ,:ivYLvr                    ,ivrrirrY2X,
#                     :;r;j5P.7r:                :ivuksxerfnli.
#                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur
#                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17
#                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i
#              :,, ,,:   ,::irii:i:::.irii:i:::j1jri7ZBOS7ivv,
#                 ,::,    ::rv77iiiriii:iii:i::,rvLrYXqZEk.Li
#             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:
#           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri
#          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:
#        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::
#        :      iuMMP: :,:::,:ii;Y#LYBB0viiii:i:iii:i:::iJqL;::
#       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii
#      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:
#     ,               ,,,,::::i:  :i:i:i:i.       ,:,, ,:::ii;i7:
#    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii
#    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::
#    i,  ,  ,8@VINCENTBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::
#    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,
#    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:
#    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::
#    :     :rkwwiBivf.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,
#     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:ia5wf88s5.,
#          , :r50EZ8MILOVEYOUBZP7::::i::,:::::,: :,:,::i;rrririiii::
#              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
#           ,:  :::,: :,,:,,,::::i:i:::::::::::,,:::::iir;ii;7v7;ii;i,
#           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiii;L8OGJrf.r;7:i,
#        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
#         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;:::i:::i:ii:::
#                          _
#                      o _|_           __
#                      |  |      (__| (__) (__(_
#                                   |

import re

try:
    import subproc
    import sqlite_base
except ModuleNotFoundError as e:
    import http_websocket.subproc as subproc
    import http_websocket.sqlite_base as sqlite_base


class CrashParser:
    def __init__(self, productname, rawdata):
        super(CrashParser, self).__init__()
        self.product_name = productname
        self.report_sql = 'ReportInfo.sqlite'
        self.build_number = str()
        self.version_number = str()
        self.proc = subproc.SubProcessBase()
        self.request_raw = bytes(rawdata)  # MUST DOCODE TO STRING BEFORE PARSING.
        self.request_lines = self.request_raw.decode().split('\n')  # SPLIT RAW DATA TO LIST

    def detect_maxtrac(self):
        """
        Detect how much lines of the Stacktrace info.
        :return: Integer, arg1: max_line_number, arg2: _id (Which line's content included the max line number, eg: -1)
        """
        _id = -1
        while True:

            try:
                max_trac = int(self.request_lines[_id].split()[0])
                return max_trac + 1, _id
            except ValueError as e:
                _id -= 1

    @staticmethod
    def get_env_info(bytes_in):
        """
        Get application information from crash content.
        :return: List object. 1)version code, 2)build number, 3)version type
        """
        # Complier regular expression
        version = re.compile(r'\d+(\.\d+){0,2}')  # version code
        build = re.compile(r'[\d]+')  # Consecutive numbers (for build number)
        type = re.compile(r'[\u4e00-\u9fa5]+')  # Match chinese (for version type)
        content = bytes_in.decode().split('\n')

        # Get info
        for i in content:
            if 'version' in i:
                print(i)
                version_code = version.search(i)
                build_number = build.findall(i)
                if type.findall(i)[0] == '正式版':
                    return [version_code.group(0), build_number[-1], 'appstore']
                else:
                    return [version_code.group(0), build_number[-1], 'dev']

    @staticmethod
    def get_apple_reason(bytes_in):
        """
        Get apple reason feedback from crash content.
        :return: String object
        """
        content = bytes_in.decode().split('\n')
        for reason in content:
            if reason.startswith('reason:') or reason.startswith('ERROR:'):
                return reason

    def get_crash_list(self):
        """
        Get any line included product_name Stacktrac information from crash content.
        :return: Two object, 1)List object. The stacktrace_list, 2)String object. CPU Arch type.
        """
        nstacktrace_max, _id = self.detect_maxtrac()
        stacktrace_list = list()
        for i in range(nstacktrace_max):
            # Get lines negative number.
            _index = _id - i
            line = self.request_lines[_index].split()
            # Get list data by reverstion.
            if self.product_name in line:
                _memory_addr_start = hex(
                    int('%s' % line[2], 16) - int(line[-1]))
                _memory_addr_stack = line[2]
                less_line = [_index, line[0], line[1],
                             _memory_addr_stack, _memory_addr_start, line[-1]]

                stacktrace_list.append(less_line)
        print('stacktrace_list', stacktrace_list)
        if stacktrace_list:
            if len(stacktrace_list[-1][3]) == 10:

                return stacktrace_list, 'armv7'
            else:
                return stacktrace_list, 'arm64'
        else:
            return 0, 0

    def atos_run(self, dSYM_file, product_name, tableid, crash_id):
        """
        Run all funciton to parsing crash info to get parameters to run atos.
        :param dSYM_file: dSYM file absolute folder address.
        :param product_name: String object, eg:WeGamers
        :return: String object
        """
        # Splicing the dSYM absolute location \
        # to get the application binary absolute location on dSYM file.
        atos = 'atos'
        arch = '-arch'
        op = '-o'
        _l = '-l'
        reason_l = list()
        app_symbol = dSYM_file + '/Contents/Resources/DWARF/%s' % product_name

        # call get_crash_list to filter what data need to parsing.
        stacktrace_list, cpu_arm_ = self.get_crash_list()

        if not stacktrace_list:
            conn, cursor = sqlite_base.sqlite_connect()
            sqlite_base.insert(conn, cursor,
                               table_name='unmatch',
                               crash_id=crash_id)
            return
        # enumerate wait to parsing data
        for _index, _value in enumerate(stacktrace_list):
            print('enumerate', _index, _value)

            # Pick memory address
            line_id = _value[0]
            stacktrac_id = _value[1]
            produce_name_raw = _value[2]
            memory_addr = _value[3]
            base_addr = _value[4]
            offset = _value[-1]
            # Parsing stack address to get the truth crash position.
            atos_cmd = ' '.join([
                atos, arch, cpu_arm_, op, app_symbol,
                _l, base_addr, memory_addr])
            print(atos_cmd)
            parse_result = self.proc.sub_procs_run(cmd=atos_cmd)
            if parse_result:
                result = parse_result.stdout.decode().replace('\n', '')
                # Data need to insert to sql.
                reason_l.append(result)
            else:
                return False
            print('atos result ', result)
            # Replace result to finally data
            replace_data = '   '.join([
                stacktrac_id, produce_name_raw, memory_addr, offset, result])
            print('replace_data', 'target line', line_id, 'data:\n', replace_data)
            print('self.data_lines[line_id]', self.request_lines[line_id])
            if '\t' in self.request_lines[line_id]:
                self.request_lines[line_id] = '\t' + replace_data
            else:
                self.request_lines[line_id] = replace_data
# Crash information insert to sql
            if tableid:
                conn, cursor = sqlite_base.sqlite_connect()
                sqlite_base.update(conn, cursor,
                                   table_name='backtrack_%d' % tableid,
                                   reason=','.join(reason_l),  # All crash information will be inserted to sql...
                                   condition="where CRASH_ID = '%s'" % crash_id)
                # print the finally data after parsing
                conn_db2, cursor_db2 = sqlite_base.sqlite_connect(self.report_sql)
                sqlite_base.insert(conn_db2, cursor_db2,
                                   table_name='report',
                                   crash_id=crash_id,
                                   log='\n'.join(self.request_lines))  # All crash information will be inserted to sql...
        return '\n'.join(self.request_lines)
