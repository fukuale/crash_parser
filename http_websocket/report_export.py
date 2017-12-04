# Author = 'Vincent FUNG'
# Create = '2017/10/10'

import collections
import datetime
import os

import time
import types
import csv

try:
    import sqlite_base
    from logger import Logger
    from similarity_compare import SimilarityCompute
    from post2jira import JIRAHandler
    from parse_crash_log import CrashParser
except ModuleNotFoundError:
    from http_websocket.logger import Logger
    import http_websocket.sqlite_base as sqlite_base
    from http_websocket.similarity_compare import SimilarityCompute
    from http_websocket.jira_handler import JIRAHandler
    from http_websocket.parse_crash_log import CrashParser

log_file = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
log = Logger(log_file, 'ReportExport')


class ReportGenerator(SimilarityCompute):
    def __init__(self, product_name_list):
        super(SimilarityCompute, self).__init__()
        self.product_name_list = product_name_list
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'database')
        self.report_sql = os.path.join(self.conf_dir, 'ReportInfo.sqlite')
        self.statistic_sql = os.path.join(self.conf_dir, 'CrashCount.sqlite')
        self.jirahandler = JIRAHandler()

    @staticmethod
    def get_today_timestamp():
        today = datetime.datetime.today() - datetime.timedelta(1)
        return str(int(time.mktime(datetime.datetime(today.year, today.month, today.day, 0, 0, 0).timetuple())))

    def get_day_from_statistics(self):
        """
        Get rowid was updated in a day from statistics table. default is yesterday.
        :return: List data. rowid list.
        """
        conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
        _big_than = sqlite_base.search(conn, cursor,
                                       columns='rowid',
                                       table_name='statistics',
                                       condition='where LAST_UPDATE > %s' % ReportGenerator.get_today_timestamp())
        if _big_than:
            return [x[0] for x in _big_than]
        else:
            return _big_than

    def get_crash_reason_all(self):
        """
        Get crash reason from backtrack tables.
        :return: Generator data. List data.
            0) table_id of backtrack tables.
            1) rowid of table.
            2) crash_id.
            3) reason.
        """
        _tables_id = self.get_day_from_statistics()
        if _tables_id:
            for table_id in _tables_id:
                conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
                _new_reason = sqlite_base.search(conn, cursor,
                                                 columns='ROWID, CRASH_ID, REASON',
                                                 table_name='backtrack_%d' % table_id,
                                                 condition='where INSERT_TIME > %s and REASON NOT NULL' %
                                                           ReportGenerator.get_today_timestamp())
                if _new_reason:
                    for _x_reason in _new_reason:
                        _x_reason = list(_x_reason)
                        _x_reason.insert(0, table_id)
                        yield list(_x_reason)  # one of list data per table.
                else:
                    log.cri(' %-20s ]-[ Table %s not match this insert time: %s' %
                            (log.get_function_name(), table_id, ReportGenerator.get_today_timestamp()))
        else:
            log.info(' %-20s ]-[ Look like have not any new crash today: %s' %
                     (log.get_function_name(), ReportGenerator.get_today_timestamp()))

    def get_crash_reason_only(self):
        """
        Make reason data only.
        :return: all tables reason. excluded duplicate data. * include crash_id, reason per data.
        """
        _only_crash_reason = list()
        _gentor = self.get_crash_reason_all()
        if _gentor:
            for _all_reason in self.get_crash_reason_all():  # Get one crash_id data
                _all_reason_clear = self.variable_remove(_all_reason[-1])  # REASON
                if _only_crash_reason:  # only list isn't empty
                    for _only_key, _only_reason in enumerate(_only_crash_reason):  # loop only list item(s).
                        _only_clear = self.variable_remove(_only_reason[-1])
                        _sim_percent = self.compute_similarity(_all_reason_clear, _only_clear)
                        if 1 == _sim_percent:
                            _table_id = _all_reason[0]
                            _table_row = _all_reason[1]
                            _only_crash_reason[_only_key][2] += 1
                            _list = _only_crash_reason[_only_key][0].get(_table_id)
                            if _list:
                                _only_crash_reason[_only_key][0][_table_id].append(_table_row)
                            else:
                                _only_crash_reason[_only_key][0][_table_id] = [_table_row]

                            break
                        if -1 == _only_key - len(_only_crash_reason):
                            _all_reason.insert(2, 1)
                            _all_reason[0] = {_all_reason[0]: [_all_reason[1]]}
                            _only_crash_reason.append(_all_reason)
                            break
                else:
                    _all_reason.insert(2, 1)
                    _all_reason[0] = {_all_reason[0]: [_all_reason[1]]}
                    _only_crash_reason.append(_all_reason)
            return _only_crash_reason
        else:
            return False

    @staticmethod
    def range_len_gen(start, end, step):
        """
        Generation loop time and remaining size.
        :param start: Startswith data size index.
        :param end: Maxium data size.
        :param step: How many data size get per time.
        :return: tuple type data. 1) loop time. for range(). 2) remaining data size. last time to get.
        """
        if step and step < end:
            _ran = (end - start) // step
            if _ran != end / step:
                yield _ran + 1, end
            else:
                yield _ran + 1, 0
        else:
            yield start, end

    @staticmethod
    def search_sql_reason(conn, cursor, _step=30, _start=1):
        """
        :param conn: Object sqlite Connection
        :param cursor: Object sqlite Cursor
        :param _step: How many data size get per time. Default=30. Because reason data is a little big.
        :param _start: Startswith data size index. Default=1
        :return: Reasons list.
        """
        _rows_count = sqlite_base.search(conn, cursor,
                                         end=False,
                                         columns='count(REASON)',
                                         table_name='reasons',
                                         condition='')
        if _rows_count:
            for ind in ReportGenerator.range_len_gen(_start, _rows_count[0][0], _step):
                for i in range(_start, ind[0] + 1):
                    if (ind[0] - _start) > 1:
                        _part_reason = sqlite_base.search(conn, cursor,
                                                          end=False,
                                                          columns='ROWID, REASON',
                                                          table_name='reasons',
                                                          condition='where rowid >= %d and rowid <= %d' % (
                                                              _start, _start + _step - 1))
                    else:
                        _part_reason = sqlite_base.search(conn, cursor,
                                                          end=False,
                                                          columns='ROWID, REASON',
                                                          table_name='reasons',
                                                          condition='where rowid >= %d and rowid <= %d' % (
                                                              _start, ind[-1]))
                    yield [_reason for _reason in _part_reason]

                    _start += _step

    def match_reason(self):
        conn, cursor = sqlite_base.sqlite_connect('Reasons.sqlite')
        conn2, cursor2 = sqlite_base.sqlite_connect()
        _income_reason_only = self.get_crash_reason_only()

        for _s_r in self.search_sql_reason(conn, cursor):
            if _s_r:
                for _s_r_s in _s_r:
                    _s_clear = self.variable_remove(_s_r_s[-1])
                    for _iro_key, _iro_value in enumerate(_income_reason_only):
                        _iro_clear = self.variable_remove(_iro_value[-1])
                        _sim_percent = self.compute_similarity(_iro_clear, _s_clear)
                        if 1 == _sim_percent:
                            del _income_reason_only[_iro_key]
                            sqlite_base.update(conn, cursor,
                                               end=False,
                                               table_name='reasons',
                                               columns=['FREQUENCY'],
                                               values=[_iro_value[2]],
                                               condition="WHERE ROWID = '%d'" % _s_r_s[0])
                            for i in _iro_value[0].keys():
                                conditions = 'WHERE '
                                _ll = _iro_value[0][i]
                                for k, v in enumerate(_ll):
                                    if k >= 1:
                                        conditions += ' or '
                                    conditions += 'ROWID = %d' % v
                                sqlite_base.update(conn2, cursor2,
                                                   end=False,
                                                   table_name='backtrack_%s' % str(i),
                                                   columns=['REASON_ID'],
                                                   values=[_s_r_s[0]],
                                                   condition=conditions)

        if conn:
            cursor.close()
            conn.close()
        if conn2:
            cursor2.close()
            conn2.close()
        if _income_reason_only:
            return _income_reason_only
        else:
            return []

    def update_jira(self):
        conn, cursor = sqlite_base.sqlite_connect('Reasons.sqlite')
        _reasons_sql_data = sqlite_base.search(conn, cursor,
                                               end=False,
                                               table_name='reasons',
                                               columns='ROWID, FIXED, JIRAID, FREQUENCY',
                                               condition='WHERE JIRAID NOT NULL')
        for _reasons in _reasons_sql_data:

            _version_new = list()
            summary = str()
            _issue = self.jirahandler.read_issue(_reasons[2])
            _biggest_version = self.sql_version(_reasons[0])[0]
            _ver_exists = _issue.fields.versions
            for k, v in enumerate(_ver_exists):
                if _biggest_version == str(v):
                    break
                if -1 == k - len(_ver_exists):
                    if len(_ver_exists) == 1:
                        _version_new.append(str(v))
                        _version_new.append(_biggest_version)
                        _version_new.sort(key=lambda x: tuple(int(v) for v in x.split('.')))
                    else:
                        _version_new[1] = _biggest_version
                    break

            _frequency_exits = _issue.fields.summary
            _frequency_string = _frequency_exits[_frequency_exits.find('[Frequency'):]
            _frequency_int = int(_frequency_string.split(':')[1].split(']')[0])

            if _reasons[-1] == _frequency_int:
                pass
            else:
                summary = _frequency_exits[:_frequency_exits.find('[Frequency')] + '[Frequency:%s]' % _reasons[-1]
            if _version_new or summary:
                self.jirahandler.update_issue(_issue, _version_new, summary)
            else:
                log.info(' %-20s ]-[ Issue %s need not to update.' % (log.get_function_name(), _reasons[-2]))
        ReportGenerator.sum_tables()

    @staticmethod
    def sql_version(reasonid):
        conn, cursor = sqlite_base.sqlite_connect()
        _tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE TYPE=\'table\' AND name LIKE \'backtrack_%\'").fetchall()
        _versions = list()
        _table = str()
        for i in _tables:
            _version = sqlite_base.search(conn, cursor,
                                          end=False,
                                          table_name=i[0],
                                          only=True,
                                          columns='VERSION',
                                          condition='WHERE REASON_ID = %s' % reasonid)
            _table = i[0]
            _versions.extend(_version)
        if _versions:
            _versions = [x[0] for x in _versions]
            _versions.sort(key=lambda x: tuple(int(v) for v in x.split('.')))
            return _versions
        else:
            log.error(' %-20s ]-[ %s cat not find REASON_ID %s .' % (log.get_function_name(), _table, reasonid))

    def submit_jira(self):
        _only_crash_id_l = self.match_reason()
        if _only_crash_id_l.__len__() > 0:
            conn, cursor = sqlite_base.sqlite_connect(self.report_sql)
            conn2, cursor2 = sqlite_base.sqlite_connect('Reasons.sqlite')
            conn3, cursor3 = sqlite_base.sqlite_connect()
            for _crash_id in _only_crash_id_l:
                _log_finally = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='LOG',
                                                  table_name='report',
                                                  condition="where CRASH_ID = '%s'" % _crash_id[-2])
                if _log_finally:
                    _rowid = int()
                    _log_l = _log_finally[0][0].split('\n')

                    __env = '\n'.join(_log_l[1:7])

                    __ver = CrashParser.get_ver_info(_log_l)[0]

                    for _lines in _log_l:
                        for x in self.product_name_list:
                            if -1 != _lines.find(x):
                                __projname = x
                                if __projname:
                                    __cr = ''.join(_lines.split()[4:])
                                    break
                        else:
                            continue
                        break
                    else:
                        continue

                    __summary = 'Crash Analysis: ' + __cr + '[Frequency:%s]' % _crash_id[1]
                    # __projname = __proj

                    _jira_id = self.jirahandler.create(pjname=__projname,
                                                       summary=__summary,
                                                       environment=__env,
                                                       description=_log_finally[0][0].replace('<pre>', '').replace(
                                                           '</pre>', ''),
                                                       version=__ver,
                                                       priority='urgen')
                    if not isinstance(_jira_id, str):
                        _rowid = sqlite_base.insert(conn2, cursor2,
                                                    end=False,
                                                    table_name='reasons',
                                                    reason=_crash_id[-1],
                                                    frequency=_crash_id[2],
                                                    jiraid=_jira_id.key)
                    else:
                        log.cri(' %-20s ]-[ Submit to JIRA error: %s .' % (log.get_function_name(), _jira_id))
                    for i in _crash_id[0].keys():
                        conditions = 'WHERE '
                        _ll = _crash_id[0][i]
                        for k, v in enumerate(_ll):
                            if k >= 1:
                                conditions += ' or '
                            conditions += 'ROWID = %d' % v
                        sqlite_base.update(conn3, cursor3,
                                           end=False,
                                           table_name='backtrack_%s' % str(i),
                                           columns=['REASON_ID'],
                                           values=[_rowid],
                                           condition=conditions)

                else:
                    log.error(' %-20s ]-[ Table report cat not find CRASH_ID %s .' %
                              (log.get_function_name(), _crash_id[-2]))
            cursor.close()
            conn.close()
        else:
            log.info(' %-20s ]-[ Look like all crash has been logged.: %s' %
                     (log.get_function_name(), ReportGenerator.get_today_timestamp()))

    @staticmethod
    def sum_tables():
        conn, cursor = sqlite_base.sqlite_connect()
        conn2, cursor2 = sqlite_base.sqlite_connect('Reasons.sqlite')
        _tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE TYPE=\'table\' AND name LIKE \'backtrack_%\'").fetchall()
        _num = int()
        for i in _tables:
            _num += int(cursor.execute("SELECT COUNT(*) FROM %s" % i).fetchall()[0][0])

        _reason = cursor2.execute("SELECT SUM(FREQUENCY) FROM reasons").fetchall()[0][0]
        log.info(' %-20s ]-[ BACKTRACK ALL ITEM: %s , REASONS ALL ITEM: %s' % (log.get_function_name(), _num, _reason))
