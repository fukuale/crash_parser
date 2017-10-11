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
    from similarity_compare import SimilarityCompute
except ModuleNotFoundError:
    import http_websocket.sqlite_base as sqlite_base
    from http_websocket.similarity_compare import SimilarityCompute


class ReportGenerator(SimilarityCompute):
    def __init__(self):
        super().__init__(0, 0)
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
                                       columns='rowid',
                                       table_name='statistics',
                                       condition='where LAST_UPDATE > %s' % ReportGenerator.get_today_timestamp())
        print(_big_than)
        return [x[0] for x in _big_than]

    def get_crash_reason_all(self):
        _tables_id = self.get_today_from_count()
        for table_id in _tables_id:
            print('table id', table_id, '\n')
            conn, cursor = sqlite_base.sqlite_connect()
            _new_reason = sqlite_base.search(conn, cursor,
                                             columns='CRASH_ID, REASON',
                                             table_name='backtrack_%d' % table_id,
                                             condition='where INSERT_TIME > %s' % ReportGenerator.get_today_timestamp())
            for _x_reason in _new_reason:
                yield _x_reason

    def get_crash_reason_only(self):
        _only_crash_reason = list()
        for _in_reason in self.get_crash_reason_all():  # Get one crash_id data
            _in_reason_clear = self.variable_remove(_in_reason[-1])
            if _only_crash_reason:  # only list isn't empty
                for _l_id, _l_value in enumerate(_only_crash_reason):  # loop only list item(s).
                    _l_id_clear = self.variable_remove(_l_value[-1])
                    _sim_percent = self.compute_similarity(_in_reason_clear, _l_id_clear)
                    if 1 == _sim_percent:
                        break
                    if -1 == _l_id - len(_only_crash_reason):
                        _only_crash_reason.append(_in_reason)
            else:
                _only_crash_reason.append(_in_reason)
        return _only_crash_reason

        # def get_report_info(self):
        #     for x in self.get_today_from_count():
        #         print('x', x)
        #         conn, cursor = sqlite_base.sqlite_connect('ReportInfo.sqlite')
        #         for crash_id in x:
        #             print('crash_id', crash_id)
        #             _rs = crash_id
        #             _res = sqlite_base.search(conn, cursor,
        #                                       end=False,
        #                                       columns='LOG',
        #                                       table_name='report',
        #                                       condition="where CRASH_ID = '%s'" % crash_id)
        #             print(_res)


if __name__ == '__main__':
    rg = ReportGenerator()
    only = rg.get_crash_reason_only()
    print(len(only), only)
    for i in only:
        _l_re = i[-1].split(',')
        print(_l_re[-1])
