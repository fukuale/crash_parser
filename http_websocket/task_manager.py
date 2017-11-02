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
#        :      iuMMP: :,:::,:ii;YRDEBB0viiii:i:iii:i:::iJqL;::
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
#          , :r50EZLEAVEMEALONEP7::::i::,:::::,: :,:,::i;rrririiii::
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

# Cause IDE need parent folder name to import other class, shell need not.
try:
    from similarity_compare import SimilarityCompute
    from get_crash_log import GetCrashInfoFromServer
    from parse_crash_log import CrashParser
    from init_dsym import DownloadDSYM
    from subproc import SubProcessBase
    from report_export import ReportGenerator
    import tornado_parser_server
except ModuleNotFoundError:
    from http_websocket.similarity_compare import SimilarityCompute
    from http_websocket.get_crash_log import GetCrashInfoFromServer
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.subproc import SubProcessBase
    from http_websocket.report_export import ReportGenerator
    import http_websocket.tornado_parser_server


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
                    yield vn.strip(), os.path.splitext(v)[0]

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
            _c_log = self.get_log.get_crash_log(version=version[0])
            yield _c_log, version[1]

    # Reparsing verson enviornment information from crash log to generation version info, product name and crash log.
    def get_env_info(self):
        """
        Parsing a part of crash log information to get the environment information.
        Generation tuple data.
        :return:
            0) env : [version_code, build_number, version_type]
            1) _ver_info[1] : Inherited from gen_version_list(), this is str(product_name)
            2) _crash_info : tuple data. [0] is crash_id, like: if-2007876330-1507164162867, [1] is crash_log.
        """
        for _ver_info in self.read_log_from_server():
            for _crash_info in _ver_info[0]:
                env = CrashParser.get_ver_info(_crash_info[-1])
                yield env, _ver_info[1], _crash_info

    def parsing(self):
        """
        Parsing crash log call.
        :return: Nothing to return.
        """
        for tuple_env_log in self.get_env_info():
            _dsym_parms = tuple_env_log[0]
            res_dSYM = self.dSYM.init_dSYM(version_number=_dsym_parms[0],
                                           build_id=_dsym_parms[1],
                                           version_type=_dsym_parms[-1],
                                           product=tuple_env_log[1])
            if res_dSYM:
                _reason = CrashParser.get_apple_reason(bytes_in=tuple_env_log[-1][-1])

                sc = SimilarityCompute(versioninfo=_dsym_parms[0], crashid=tuple_env_log[-1][0])
                _row_id = sc.apple_locate_similarity(_reason)

                _ins_parser = CrashParser(productname=tuple_env_log[1], rawdata=tuple_env_log[-1][-1])
                _ins_parser.atos_run(dSYM_file=res_dSYM,
                                     product_name=tuple_env_log[1],
                                     tableid=_row_id,
                                     crash_id=tuple_env_log[-1][0])

    def jira(self):
        _project_name_l = [os.path.splitext(x)[0] for x in self.conf_files]
        rg = ReportGenerator(product_name_list=_project_name_l)
        rg.submit_jira()
        rg.update_jira()


if __name__ == '__main__':
    ts = TaskSchedule()
    ts.parsing()
    ts.jira()
