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
    def __init__(self, productname, rawdata):
        super(CrashParser, self).__init__()
        self.build_number = str()
        self.version_number = str()
        self.product_name = productname
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

    def get_env_info(self):
        """
        Get application information from crash content.
        :return: List object. 1)version code, 2)build number, 3)version type
        """
        # Complier regular expression
        version = re.compile(r'\d+(\.\d+){0,2}')  # version code
        build = re.compile(r'[\d]+')  # Consecutive numbers (for build number)
        type = re.compile(r'[\u4e00-\u9fa5]+')  # Match chinese (for version type)

        # Get info
        for i in self.request_lines:
            if 'version' in i:
                version_code = version.search(i)
                build_number = build.findall(i)
                if type.findall(i)[0] == '正式版':
                    print([version_code.group(0), build_number[-1], 'appstore'])
                    return [version_code.group(0), build_number[-1], 'appstore']
                else:
                    print([version_code.group(0), build_number[-1], 'dev'])
                    return [version_code.group(0), build_number[-1], 'dev']

    def get_apple_reason(self):
        """
        Get apple reason feedback from crash content.
        :return: String object
        """
        for i in self.request_lines:
            if i.startswith('reason:') or i.startswith('ERROR:'):
                return i

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
        if len(stacktrace_list[-1][3]) == 10:

            return stacktrace_list, 'armv7'
        else:
            return stacktrace_list, 'arm64'

    def atos_run(self, dSYM_file, product_name):
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
        app_symbol = dSYM_file + '/Contents/Resources/DWARF/%s' % product_name

        # call get_crash_list to filter what data need to parsing.
        stacktrace_list, cpu_arm_ = self.get_crash_list()

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
            result = parse_result.stdout.decode().replace('\n', '')
            # Replace result to finally data
            replace_data = '   '.join([
                line_id_raw, produce_name_raw, memory_addr, offset, result])
            print('replace_data', 'target line', line_id, 'data:\n', replace_data)
            print('self.data_lines[line_id]', self.request_lines[line_id])
            self.request_lines[line_id] = '    ' + replace_data

        # print the finally data after parsing
        print('\n'.join(self.request_lines))


if __name__ == '__main__':
    data = b"<pre>=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPhone 5 (GSM+CDMA)\nIOS Ver:            iPhone OS 8.4.1\navailableMemory:    103.5MB\nusedMemory:         53.3MB\ntime:               2017-09-27_16-13-07\nnUid:               0\nsName:              \nsLinkID:            \nsBindEmail:         \nphone:              \n\nERROR: All calls to UIKit need to happen on the main thread. You have a bug in your code. Use dispatch_async(dispatch_get_main_queue(), ^{ ... }); if you're unsure what thread you're in.\n\nBreak on PSPDFAssertIfNotMainThread to find out where.\n\nStacktrace: (\n\t0   WeGamers                            0x00aa32ed WeGamers + 10707693\n\t1   WeGamers                            0x00aa334b WeGamers + 10707787\n\t2   UIKit                               0x271bb105 <redacted> + 164\n\t3   UIKit                               0x26e4a719 <redacted> + 164\n\t4   MediaPlayer                         0x2504563f <redacted> + 994\n\t5   MediaPlayer                         0x25043f95 <redacted> + 212\n\t6   MediaPlayer                         0x25044029 <redacted> + 80\n\t7   MediaPlayer                         0x25043fd3 <redacted> + 38\n\t8   UIKit                               0x26e12f39 <redacted> + 44\n\t9   WebCore                             0x2ff57165 <redacted> + 264\n\t10  WebCore                             0x2ff57417 <redacted> + 394\n\t11  WebCore                             0x2ff56541 <redacted> + 172\n\t12  WebCore                             0x2ff5642d _ZN7WebCore19MediaSessionManager13sharedManagerEv + 124\n\t13  WebCore                             0x2ff5567d <redacted> + 32\n\t14  WebCore                             0x2fbe5235 <redacted> + 20\n\t15  WebCore                             0x2fbd3b37 <redacted> + 1046\n\t16  WebCore                             0x2fbb80f1 <redacted> + 36\n\t17  WebCore                             0x2fbc652d <redacted> + 56\n\t18  WebCore                             0x2fbc63d9 <redacted> + 232\n\t19  WebCore                             0x2f822a1b <redacted> + 126\n\t20  WebCore                             0x2f8228c5 <redacted> + 20\n\t21  WebCore                             0x2f821c9d <redacted> + 2660\n\t22  WebCore                             0x2f82087d <redacted> + 2224\n\t23  WebCore                             0x2f81ff35 <redacted> + 88\n\t24  WebCore                             0x2f81fe45 <redacted> + 212\n\t25  WebCore                             0x2f81f845 <redacted> + 104\n\t26  WebCore                             0x2f80f8e3 <redacted> + 334\n\t27  WebCore                             0x2f8d3b41 <redacted> + 20\n\t28  WebCore                             0x2f7c78dd <redacted> + 132\n\t29  WebCore                             0x2f7c7839 <redacted> + 24\n\t30  CoreFoundation                      0x23739cbf <redacted> + 14\n\t31  CoreFoundation                      0x2373983b <redacted> + 650\n\t32  CoreFoundation                      0x23737a8b <redacted> + 1418\n\t33  CoreFoundation                      0x23683f31 CFRunLoopRunSpecific + 476\n\t34  CoreFoundation                      0x23683d43 CFRunLoopRunInMode + 106\n\t35  WebCore                             0x2f82b98b <redacted> + 418\n\t36  libsystem_pthread.dylib             0x3251be17 <redacted> + 138\n\t37  libsystem_pthread.dylib             0x3251bd8b _pthread_start + 118\n\t38  libsystem_pthread.dylib             0x32519b14 thread_start + 8\n)</pre>"
    dSYM = '/Users/vincent/Downloads/WeGamers_11311.DSYM'
    cp = CrashParser(productname='WeGamers', rawdata=data)
    # cp.get_env_info()
    cp.atos_run(dSYM_file=dSYM, product_name='WeGamers')
