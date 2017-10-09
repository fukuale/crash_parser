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


import os

try:
    from similarity_compare import SimilarityCompute
    from get_crash_log import GetCrashInfoFromServer
    from parse_crash_log import CrashParser
    from init_dsym import DownloadDSYM
    from subproc import SubProcessBase
    import tornado_parser_server
except ModuleNotFoundError:
    from http_websocket.similarity_compare import SimilarityCompute
    from http_websocket.get_crash_log import GetCrashInfoFromServer
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.subproc import SubProcessBase
    import http_websocket.tornado_parser_server


class TaskSchedule(object):
    def __init__(self):
        super(TaskSchedule, self).__init__()
        # Get configuration file, product name.
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'conf')
        # Get all the configuration files under [CrashParser] path
        self.conf_files = [z for a, b, x in os.walk(self.conf_dir) for z in x if
                           not z.startswith('_') and not z.startswith('.')]

        # Variable type define
        self.crash_info_env = list()
        self.current_app_name = int()
        self.dSYM_abspath = str()
        self.parser_wait_raw = str()

        # Instance needed class
        self.get_log = GetCrashInfoFromServer()
        self.dSYM = DownloadDSYM()

    # Generation the product name and version that need to parsing
    def gen_version_list(self):
        print(self.conf_files)
        for k, v in enumerate(self.conf_files):
            print(k, v)
            _v_list = open(os.path.join(self.conf_dir, v), 'r', encoding='utf-8').readlines()
            for vn in _v_list:
                if vn:
                    yield vn.strip(), os.path.splitext(v)[0]

    # Get the crash log generator
    def read_log_from_server(self):
        for version in self.gen_version_list():
            _c_log = self.get_log.get_crash_log(version=version[0])
            yield _c_log, version[1]

    # Reparsing verson enviornment information from crash log to generation version info, product name and crash log.
    def get_env_info(self):
        for _ver_info in self.read_log_from_server():
            for _crash_info in _ver_info[0]:
                print(_crash_info)
                env = CrashParser.get_env_info(_crash_info[-1])
                yield env, _ver_info[1], _crash_info

    def parsing(self):
        for tuple_env_log in self.get_env_info():
            print('tuple_env_log', tuple_env_log)
            print(tuple_env_log[-1][0])
            _dsym_parms = tuple_env_log[0]
            res_dSYM = self.dSYM.init_dSYM(version_number=_dsym_parms[0],
                                           build_id=_dsym_parms[1],
                                           version_type=_dsym_parms[-1],
                                           product=tuple_env_log[1])
            print('res_dSYM', res_dSYM)
            if res_dSYM:
                _reason = CrashParser.get_apple_reason(bytes_in=tuple_env_log[-1][-1])
                print('_reason', _reason)

                sc = SimilarityCompute(versioninfo=_dsym_parms[0], crashid=tuple_env_log[-1][0])
                _row_id = sc.apple_locate_similarity(_reason)
                print('_row_id', _row_id)

                _ins_parser = CrashParser(productname=tuple_env_log[1], rawdata=tuple_env_log[-1][-1])
                _ins_parser.atos_run(dSYM_file=res_dSYM,
                                     product_name=tuple_env_log[1],
                                     tableid=_row_id,
                                     crash_id=tuple_env_log[-1][0])



if __name__ == '__main__':
    process = []

    # process.append(start_service)
    ts = TaskSchedule()
    ts.parsing()
        # ts.test()
        # ts.start_service()
        # ts.dSYM_need_not()
        # ts.parse()
