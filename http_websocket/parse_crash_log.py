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

import subprocess
import sqlite3
import re

try:
    import subproc
    import sqlite_base
except ModuleNotFoundError as e:
    import http_websocket.subproc as subproc
    from http_websocket import sqlite_base


class CrashParser:
    def __init__(self, producename, rawdata):
        super(CrashParser, self).__init__()
        self.build_number = str()
        self.version_number = str()
        self.produce_name = producename
        self.proc = subproc.SubProcessBase()
        self.request_raw = bytes(rawdata)  # MUST DOCODE TO STRING BEFORE PARSING.
        self.data_lines = self.request_raw.decode().split('\n')  # SPLIT RAW DATA TO LIST

    def detect_maxtrac(self):
        """
        Detect how much lines of the Stacktrace info.
        :return: arg1: max_line_number, arg2: _id (Which line's content included the max line number, eg: -1)
        """
        _id = -1
        while False:

            try:
                max_trac = int(self.data_lines[_id].split()[0])
                return int(
                    self.data_lines[max_trac].split()[0]) + 1, _id
            except ValueError as e:
                _id -= 1
                break
            finally:
                # TODO WRITE DETECT FAILED LOG AND LINE CONTENT.
                pass

    def get_env_info(self):

        # Complier regular expression
        version = re.compile(r'\d+(\.\d+){0,2}')  # version code
        build = re.compile(r'[\d]+')  # Consecutive numbers (for build number)
        type = re.compile(r'[\u4e00-\u9fa5]+')  # Match chinese (for version type)

        # Get info
        for i in self.data_lines:
            if 'version' in i:
                version_code = version.search(i)
                build_number = build.findall(i)
                if type.findall(i)[0] == '正式版':
                    print('正式版', type.findall(i))
                    version_type = 'appstore'
                else:
                    print('dev版', type.findall(i))
                    version_type = 'dev'
                    return [version_code.group(0), build_number[-1], version_type]

    def get_apple_reason(self):
        for i in self.data_lines:
            if i.startswith('reason:') or i.startswith('ERROR:'):
                return i

    def cpu_arch(self):
        if len(self.data_lines[-5].split()[2]) == 10:

            return 'armv7'
        else:
            return 'arm64'

    # Get Stacktrac list and seqencing.
    def get_crash_list(self):
        nstacktrace_max, _id = self.detect_maxtrac()
        stacktrace_list = list()
        for i in range(nstacktrace_max):
            # Get lines negative number.
            _index = _id - i
            line = self.data_lines[_index].split()
            # Get list data by reverstion.
            if self.produce_name in line:
                _memory_addr_start = hex(
                    int('%s' % line[2], 16) - int(line[-1]))
                _memory_addr_stack = line[2]
                less_line = [_index, line[0], line[1],
                             _memory_addr_stack, _memory_addr_start, line[-1]]

                stacktrace_list.append(less_line)
        return stacktrace_list

    @staticmethod
    def hex_verify(_unknow_type):
        try:
            int(_unknow_type, 16)
        except ValueError as e:
            return False

    def compute_similarity(self):
        # Parameters init
        a = str()
        ver = str()
        _first_match = list()
        _compared_data = list()

        # Get apple reason and split to list
        _reason = self.get_apple_reason().split()

        # Set standard percentage of similarity in this case
        if len(_reason) <= 10:
            _stand_percent = 0.5
        else:
            _stand_percent = 0.7

        # Connect to sqlite
        conn, cursor = sqlite_base.sqlite_connect()

        # Match first word matched data from sqlite
        for i in range(1, len(_reason)):
            _unknow_type = _reason[i]
            if not self.hex_verify(_unknow_type):
                _first_match = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  colums='ID, COUNT, CONTENT',
                                                  table_name='statistics',
                                                  condition="where CONTENT LIKE \'%%%s%%\'" % _unknow_type)
                break
            else:
                for i in self.data_lines:
                    if 'version' in i:

                        break
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='statistics',
                                   fixed='0',
                                   count='1',
                                   content=i,
                                   fv=ver,
                                   lv=None)

        # Loop match data from sqlite and compute the percentage of similarity.
        for i in _first_match:
            # Per line data
            _target = i[-1].split()
            _mm = [a for x in _reason if x in _target]
            _percent_compute = float(len(_mm) / (len(_target) + len(_reason) / 2))
            if _percent_compute > _stand_percent:
                _compared_data.append((_percent_compute, i[0], i[1], _target))
            else:
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='statistics',
                                   fixed='0',
                                   count='1',
                                   content=i,
                                   fv=ver,
                                   lv=None)

        _compared_data = _compared_data.sort(key=lambda x: x[0])

        sqlite_base.update(conn, cursor,
                           colums=['ID', 'COUNT'],
                           values=[_compared_data[-1][1], _compared_data[-1][2]])
        if conn:
            if cursor:
                cursor.close()
            conn.close()

    def atos_run(self, dSYM_file, product_name):
        # Splicing the dSYM absolute location \
        # to get the application binary absolute location on dSYM file.
        atos = 'atos'
        arch = '-arch'
        op = '-o'
        _l = '-l'
        app_symbol = dSYM_file + '/Contents/Resources/DWARF/%s' % product_name

        # call get_crash_list to filter what data need to parsing.
        stacktrace_list = self.get_crash_list()

        # Get cpu arch
        cpu_arm_ = self.cpu_arch()

        # enumerate wait to parsing data
        for _index, _value in enumerate(stacktrace_list):
            print('enumerate', _index, _value)

            # Pick memory address
            line_id = _value[0]
            line_id_raw = _value[1]
            produce_name_raw = _value[2]
            memory_addr = _value[3]
            base_addr = _value[4]
            offset = _value[-1]
            # Parsing memory address to get the truth method called
            atos_cmd = ' '.join([
                atos, arch, cpu_arm_, op, app_symbol,
                _l, base_addr, memory_addr])
            print(atos_cmd)
            parse_result = self.proc.sub_procs_run(cmd=atos_cmd)
            result = parse_result.stdout.decode()
            # Replace result to finally data
            replace_data = '    '.join([
                line_id_raw, produce_name_raw, memory_addr, offset, result])
            print('replace_data', 'target line', line_id, 'data:\n', replace_data)
            print('self.data_lines[line_id]', self.data_lines[line_id])
            self.data_lines[line_id] = replace_data

        # print the finally data after parsing
        self.compute_similarity()
        print('\n'.join(self.data_lines))
