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
    def get_today_timestamp(day=9):
        today = datetime.datetime.today() - datetime.timedelta(day)
        return str(int(time.mktime(datetime.datetime(today.year, today.month, today.day, 0, 0, 0).timetuple())))

    def get_today_from_count(self):
        """

        :return: backtrack_x tables id.
        """
        conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
        _big_than = sqlite_base.search(conn, cursor,
                                       columns='rowid',
                                       table_name='statistics',
                                       condition='where LAST_UPDATE > %s' % ReportGenerator.get_today_timestamp())
        print(_big_than)
        if _big_than:
            return [x[0] for x in _big_than]
        else:
            return _big_than

    def get_crash_reason_all(self):
        """

        :return: all tables reason. included duplicate data.
            1) CRASH_ID
            2) REASON
        """
        _tables_id = self.get_today_from_count()
        if _tables_id:
            for table_id in _tables_id:
                print('table id', table_id)
                conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
                _new_reason = sqlite_base.search(conn, cursor,
                                                 columns='CRASH_ID, REASON',
                                                 table_name='backtrack_%d' % table_id,
                                                 condition='where INSERT_TIME > %s' % ReportGenerator.get_today_timestamp())
                if _new_reason:
                    for _x_reason in _new_reason:
                        yield _x_reason  # one of list data per table.
                else:
                    return _tables_id
        else:
            return _tables_id

    def get_crash_reason_only(self):
        """

        :return: all tables reason. excluded duplicate data.
        """
        _only_crash_reason = list()
        _gentor = self.get_crash_reason_all()
        if _gentor:
            for _all_reason in self.get_crash_reason_all():  # Get one crash_id data
                _all_reason_clear = self.variable_remove(_all_reason[-1])  # REASON
                if _only_crash_reason:  # only list isn't empty
                    for _only_key, _only_reason in enumerate(_only_crash_reason):  # loop only list item(s).
                        _only_clear = self.variable_remove(_only_reason)
                        _sim_percent = self.compute_similarity(_all_reason_clear, _only_clear)
                        if 1 == _sim_percent:
                            break
                        if -1 == _only_key - len(_only_crash_reason):
                            _only_crash_reason.append(_all_reason[-1])
                else:
                    _only_crash_reason.append(_all_reason[-1])
            return _only_crash_reason
        else:
            return _gentor

    @staticmethod
    def search_sql_reason(conn, cursor):
        _rows = sqlite_base.search(conn, cursor,
                                   columns='count(REASON)',
                                   table_name='reasons',
                                   condition='')
        if _rows > 100:
            _ran = int()
            _x = _rows / 100
            _z = _rows // 100
            if _x != _z:
                _ran = _z + 1
            else:
                _ran = _z
            for i in range(1, _ran):
                _part_reason = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='REASON',
                                                  table_name='reasons',
                                                  condition='where rowid > %d and rowid < %d' % (_ran, _rows - _ran))
                yield [x[0] for x in _part_reason]
        else:
            return False

    def match_sql(self):
        conn, cursor = sqlite_base.sqlite_connect('Reasons.sqlite')
        _only_re = self.get_crash_reason_only()
        _sql_gen = self.search_sql_reason(conn, cursor)
        print('cccccc', '\n', _only_re)
        if _sql_gen and _only_re:
            for _sr in _sql_gen:
                print('srsrsrsr', _sr)
                _sql_clear = self.variable_remove(_sr)
                for k, v in enumerate(_only_re):
                    print('kvkvkv',k,v)
                    _or_clear = self.variable_remove(v)
                    _sim_percent = self.compute_similarity(_sql_clear, _or_clear)
                    if 1 == _sim_percent:
                        del _only_re[k]
                    else:
                        pass
            if _only_re:
                return _only_re
            else:
                return []

    def gen_csv_report(self):
        _only_crash_id_l = self.match_sql()
        if _only_crash_id_l.__len__() > 0:
            for _crash_id in _only_crash_id_l:
                conn, cursor = sqlite_base.sqlite_connect(self.report_sql)
                _log_finally = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='LOG',
                                                  table_name='report',
                                                  condition="where CRASH_ID = '%s'" % _crash_id)
                if _log_finally:
                    print(_log_finally)
                else:
                    print('csv report generation failed !')
        else:
            print('Have no new crash now !')


if __name__ == '__main__':
    rg = ReportGenerator()
    rg.gen_csv_report()

