# Author = 'Vincent FUNG'
# Create = '2017/10/10'
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
import datetime
import os

import time

try:
    import sqlite_base
except ModuleNotFoundError:
    import http_websocket.sqlite_base as sqlite_base


class ReportGenerator(object):
    def __init__(self):
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'database')
        self.report_sql = os.path.join(self.conf_dir, 'ReportInfo.sqlite')
        self.statistic_sql = os.path.join(self.conf_dir, 'CrashCount.sqlite')

    @staticmethod
    def get_today_timestamp(day=1):
        today = datetime.datetime.today() - datetime.timedelta(day)
        return str(int(time.mktime(datetime.datetime(today.year, today.month, today.day, 0, 0, 0).timetuple())))

    @staticmethod
    def get_today_from_count():
        conn, cursor = sqlite_base.sqlite_connect()
        _big_than = sqlite_base.search(conn, cursor,
                                       end=False,
                                       columns='rowid',
                                       table_name='statistics',
                                       condition='where LAST_UPDATE > %s' % ReportGenerator.get_today_timestamp())
        print(_big_than)
        return [x[0] for x in _big_than]

    def get_crash_id(self):
        _tables_id = self.get_today_from_count()
        for table_id in _tables_id:
            conn, cursor = sqlite_base.sqlite_connect()
            _id_l = sqlite_base.search(conn, cursor,
                                       columns='CRASH_ID',
                                       table_name='backtrack_%d' % table_id,
                                       condition='where INSERT_TIME > %s' % ReportGenerator.get_today_timestamp())
            yield _id_l

    def get_report_info(self):
        for x in self.get_crash_id():
            conn, cursor = sqlite_base.sqlite_connect('ReportInfo.sqlite')
            print('x', x)
            for crash_id in x:
                print('crash_id[0]', crash_id[0])
                _res = conn, cursor = sqlite_base.search(conn, cursor,
                                                         end=False,
                                                         columns='LOG',
                                                         table_name='report',
                                                         condition='where CRASH_ID = "%s"' % crash_id[0])
                print(type(_res))


if __name__ == '__main__':
    rg = ReportGenerator()
    rg.get_report_info()
