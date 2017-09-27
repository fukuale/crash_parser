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

import multiprocessing
import gevent

# from parser_crash_info import Crash_Parser
# from init_dsym import DownloadDSYM

from parse_crash_log import CrashParser
from init_dsym import DownloadDSYM
from subproc import SubProcessBase
import tornado_parser_server


class TaskSchedule(object):
    """docstring for TaskSchedule"""

    def __init__(self):
        super(TaskSchedule, self).__init__()
        self.packages_name = ['WeGamers', 'GameLive', 'Link']
        self.crash_data_clear = list()
        self.crash_info_env = list()
        self.crash_info_stacktrac = list()
        self.crash_info_parse = list()
        self.current_app_name = int()
        self.dSYM_abspath = str()
        self.parser_wait_raw = str()

        self.parser = CrashParser(
            packagenames=self.packages_name,
            rawdata=self.parser_wait_raw
        )
        self.dSYM = DownloadDSYM()
        self.parser.get_crash_info(pkgname=self.packages_name)
        self.subproc = SubProcessBase()

    def dSYM_need_not(self):
        self.crash_info_env = self.parser.get_env_info()
        print(self.crash_info_env)
        is_dSYM = self.dSYM.init_dSYM(build_id=self.crash_info_env[1],
                                      version_number=self.crash_info_env[0],
                                      version_type=self.crash_info_env[2],
                                      product=self.packages_name[self.current_app_name]
                                      )
        if is_dSYM:
            self.dSYM_abspath = is_dSYM
        else:
            print('something went wrong... can\'t detected any dSYM file compare this case.')

    def parse(self):
        self.parser.call_atos(dSYM_file=self.dSYM_abspath,
                              product_name=self.packages_name[self.current_app_name],
                              proc=self.subproc)

    def start_service(self):
        tornado_parser_server.run()


if __name__ == '__main__':
    process = []
    # process.append(start_service)
    ts = TaskSchedule()
    ts.start_service()
    ts.dSYM_need_not()
    ts.parse()
