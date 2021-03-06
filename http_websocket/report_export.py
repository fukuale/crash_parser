# Author = 'Vincent FUNG'
# Create = '2017/10/10'

import collections
import datetime
import os
import time
import jira

from . import regular_common
from . import sqlite_base
from .jira_handler import JIRAHandler
from .logger import Logger
from .parse_crash_log import CrashParser
from .parser_exception import BreakProcessing
from .similarity_compare import SimilarityCompute

LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'ReportExport')


class ReportGenerator(SimilarityCompute):
    """Filter all the issue need to commit/update.
    """
    def __init__(self, product_name_list):
        SimilarityCompute.__init__(self, 0, 0, 0)
        self.product_name_list = product_name_list
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'database')
        self.jirahandler = JIRAHandler()

    @staticmethod
    def get_yesterday_timestamp(day=1):
        """Compute the timestamp for someday.

        Keyword Arguments:
            day {int} -- [This is the number days before from today.] (default: {1})

        Returns:
            [String] -- [The timestamp of the day.]
        """
        today = datetime.datetime.today() - datetime.timedelta(day)

        return str(
            int(time.mktime(                     #将时间元组转化为时间戳
                datetime.datetime(
                    today.year, today.month, today.day, 0, 0, 0).timetuple())))

    def get_day_from_statistics(self):
        """Get all the rows updated later than some day from statistics table.

        Returns:
            [List] -- [The rowid list.]
        """
        conn, cursor = sqlite_base.sqlite_connect()
        # conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
        _later_than = sqlite_base.search(conn, cursor,
                                         columns='rowid',
                                         table_name='statistics',
                                         condition='where LAST_UPDATE > %s' % ReportGenerator.get_yesterday_timestamp())
        if _later_than:
            return [x[0] for x in _later_than]   #?
        else:
            return _later_than

    def get_specific_range_crashes(self):
        """Get all the crash reason from backtrack tables.

        Yields:
            [List] -- 0) The id of backtrack tables.
                       1) rowid of table.
                       2) crash_id.
                      3) project name.
                      4) reason.
        """
        _tables_id = self.get_day_from_statistics()
        if _tables_id:
            for table_id in _tables_id:
                conn, cursor = sqlite_base.sqlite_connect()
                # conn, cursor = sqlite_base.sqlite_connect(sql_abs_path=self.statistic_sql)
                _new_reason = sqlite_base.search(conn, cursor,
                                                 columns='ROWID, CRASH_ID, PROJECT, REASON',
                                                 table_name='backtrack_%d' % table_id,
                                                 condition='where INSERT_TIME > %s and REASON NOT NULL' %
                                                           ReportGenerator.get_yesterday_timestamp())
                if _new_reason:
                    for _x_reason in _new_reason:
                        _x_reason = list(_x_reason)
                        _x_reason.insert(0, table_id)      #0为插入位置
                        yield list(_x_reason)
                else:
                    LOG.cri(' %-20s ]-[ Table %s not match this insert time: %s' %
                            (LOG.get_function_name(), table_id, ReportGenerator.get_yesterday_timestamp()))
        else:
            # TODO: SQLITE ERROR MESSAGE NOT COMPLETED YET. THAT WILL LET THE LOGIC EXCEPTION IN THE CALL METHOD.
            LOG.info(' %-20s ]-[ Look like have not any new crash today: %s' %
                     (LOG.get_function_name(), ReportGenerator.get_yesterday_timestamp()))

    def make_uniquenesss_list(self, datain):      #[(table_id, ROWID, CRASH_ID, PROJECT, REASON),()]
        """Make a list exclude the duplicate data.
        
        Arguments:
            datain {List} -- 0) The id of backtrack tables.
                             1) rowid of table.
                             2) crash_id.
                             3) project name.
                             4) reason.

        Returns:
            List -- all tables reason. excluded duplicate data. complex data struct..
        """
        # Define clear list.
        _only_crash_reason = list()                      #_only_crash_reason?

        if isinstance(datain, collections.Iterable):
            for _per_reason in datain:
                # Clean data.
                _clear_reason = self.mutable_remove(_per_reason[-1])
                # Remove that data isn't match of the project with current datain.
                _only_target = [x for x in _only_crash_reason if _per_reason[-2] or 'StreamCraft' in x]

                if _only_target.__len__() != 0:
                    # Traverse list to compute similarity.
                    for _only_key, _only_reason in enumerate(_only_target):
                        # Clean the data from clear list.
                        _only_clear = self.mutable_remove(_only_reason[-1])
                        # Compute.
                        _sim_percent = self.compute_similarity(_clear_reason, _only_clear)
                        # 100% math.
                        if _sim_percent == 1:
                            _table_id = _per_reason[0]
                            _table_row = _per_reason[1]
                            # Frequency count.
                            _only_crash_reason[_only_key][2] += 1
                            _tb_id = _only_crash_reason[_only_key][0].get(_table_id)
                            if _tb_id:
                                # Log row and the table id of the duplicate data.
                                _only_crash_reason[_only_key][0][_table_id].append(_table_row)
                            else:
                                _only_crash_reason[_only_key][0][_table_id] = [_table_row]

                            break
                        # Insert this data once traverse to the list of the last one still can not 100% match.
                        if -1 == _only_key - len(_only_crash_reason):
                            _per_reason.insert(2, 1)
                            _per_reason[0] = {_per_reason[0]: [_per_reason[1]]}
                            _only_crash_reason.append(_per_reason)
                            break
                else:
                    _per_reason.insert(2, 1)
                    _per_reason[0] = {_per_reason[0]: [_per_reason[1]]}   # {_table_id:rowid}
                    _only_crash_reason.append(_per_reason)         #[{tableid:rowid}, ROWID, 1, CRASH_ID, PROJECT, REASON),()]
            return _only_crash_reason

    @staticmethod
    def range_len_gen(start, end, step):
        """Generation loop time and remaining size.

        Arguments:
            start {Integer} -- [Startswith data size index.]
            end {Integer} -- [Maxium data size.]
            step {Integer} -- [How many data size get per time.]

        Yields:
            [Tuple] -- [1) loop time. for range(). 2) remaining data size. last time to get.]
        """
        if step and step < end:
            _ran = (end - start) // step     #结果为整数
            if _ran != end / step:
                yield _ran + 1, end
            else:
                yield _ran + 1, 0
        else:
            yield start, end

    @staticmethod
    def search_sql_reason(conn, cursor, _step=30, _start=1):
        """Get reasons from reasons table.

        Arguments:
            conn {Sqlite3.Connection} -- [The sqlite connection.]
            cursor {Sqlite3.Cusor} -- [The sqlite cursor.]

        Keyword Arguments:
            _step {Integer} -- [How many data want to get per time.] (default: {30})
            _start {Integer} -- [Startswith data size index.] (default: {1})
        """
        # Get the table reasons rows number.
        _rows_count = sqlite_base.search(conn, cursor,
                                         end=False,
                                         columns='count(REASON)',
                                         table_name='reasons',
                                         condition='')
        if _rows_count:
            # Limit the search result data size on max 30.
            for ind in ReportGenerator.range_len_gen(_start, _rows_count[0][0], _step):          #_(ran + 1, 0)
                # Uhmmmm.. I forgot why i write the following line...
                for i in range(_start, ind[0] + 1):
                    # Search part of data. Limit memory usage.
                    if (ind[0] - _start) > 1:
                        _part_reason = sqlite_base.search(conn, cursor,
                                                          end=False,
                                                          columns='ROWID, PROJECT, REASON',
                                                          table_name='reasons',
                                                          condition='where rowid >= %d and rowid <= %d' % (
                                                              _start, _start + _step - 1))
                    else:
                        # Data lenght small than step. Get all at once.
                        _part_reason = sqlite_base.search(conn, cursor,
                                                          end=False,
                                                          columns='ROWID, PROJECT, REASON',
                                                          table_name='reasons',
                                                          condition='where rowid >= %d and rowid <= %d' % (
                                                              _start, ind[-1]))
                    yield [_reason for _reason in _part_reason]

                    _start += _step

    def match_reason(self):
        """Match tables reasons data with today's data.
        And update releation data.

        Returns:
            List -- The reasons need to submit to JIRA server.
        """
        conn, cursor = sqlite_base.sqlite_connect()
        # Read today crashes reasons.
        _td_reasons = self.get_specific_range_crashes()         #[table_id, ROWID, CRASH_ID, PROJECT, REASON]
        # Remove duplicate data.
        _uniqueness_l = self.make_uniquenesss_list(_td_reasons)    #[{tableid:rowid}, ROWID, 1, CRASH_ID, PROJECT, REASON),()]
        # Get all the reasons that has been logged.
        for _reason in self.search_sql_reason(conn, cursor):   #[(ROWID, PROJECT, REASON), ()]
            if _reason.__len__() != 0:
                for _per_reason in _reason:
                    # Clean that reason from table reasons.
                    _s_clear = self.mutable_remove(str(_per_reason[-2:]))    #_per_reason[-2:]要改成_per_reason[-1]吧
                    # Traverse today's reasons list.
                    for _iro_key, _iro_value in enumerate(_uniqueness_l):
                        # Clean that reason from today's list.
                        _iro_clear = self.mutable_remove(str(_iro_value[-2:]))       #同上
                        # Compute similarity.
                        _sim_percent = self.compute_similarity(_iro_clear, _s_clear)
                        if _sim_percent == 1:
                            del _uniqueness_l[_iro_key]
                            # Update frequency once 100% match.
                            sqlite_base.update(conn, cursor,
                                               end=False,
                                               table_name='reasons',
                                               columns=['FREQUENCY'],
                                               values=[_iro_value[2]],
                                               condition="WHERE ROWID = '%d'" % _per_reason[0])
                            # Update that all tables data releation with this reason.
                            for i in _iro_value[0].keys():
                                conditions = 'WHERE '
                                _ll = _iro_value[0][i]
                                for key, value in enumerate(_ll):
                                    if key >= 1:
                                        conditions += ' or '
                                    conditions += 'ROWID = %d' % value
                                sqlite_base.update(conn, cursor,
                                                   end=False,
                                                   table_name='backtrack_%s' % str(i),
                                                   columns=['REASON_ID'],
                                                   values=[_per_reason[0]],
                                                   condition=conditions)

        if conn:
            cursor.close()
            conn.close()
        if _uniqueness_l.__len__() != 0:
            # This list is the new crash relative to old data
            return _uniqueness_l
        else:
            # Empty means today's crash already submitted to JIRA server.
            return []

    @staticmethod
    def get_max_version(reasonid):
        """[summary]

        Arguments:
            reasonid {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        _versions = list()

        conn, cursor = sqlite_base.sqlite_connect()
        # Get all the backtrack_x tables list.
        _tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE TYPE=\'table\' AND name LIKE \'backtrack_%\'").fetchall()
        for i in _tables:
            # Get the uniqueness version from backtrack tabels.
            _version = sqlite_base.search(conn, cursor,
                                          end=False,
                                          table_name=i[0],
                                          only=True,
                                          columns='VERSION',
                                          condition='WHERE REASON_ID = %s' % reasonid)
            _versions.extend(_version)
        if _versions.__len__() != 0:
            _versions = [x[0] for x in _versions]
            # Sort version list by ASC.
            _versions.sort(key=lambda x: tuple(int(v) for v in x.split('.')))
            return _versions
        else:
            LOG.error(' %-20s ]-[ All backtrack tables both cat not find REASON_ID %s .' % (LOG.get_function_name(), reasonid))


    def update_jira(self, que):
        """Update JIRA issue.
        """
        conn, cursor = sqlite_base.sqlite_connect()
        # conn, cursor = sqlite_base.sqlite_connect('Reasons.sqlite')
        # Get the reason that already submitted to JIRA yet.
        _reasons_sql_data = sqlite_base.search(conn, cursor,
                                               end=False,
                                               table_name='reasons',
                                               columns='ROWID, FIXED, JIRAID, FREQUENCY',
                                               condition='WHERE JIRAID NOT NULL')
                                        
        if not isinstance(_reasons_sql_data, collections.Iterable):
            raise BreakProcessing('No new issue(s) need to submit.')

        for index, _reasons in enumerate(_reasons_sql_data):
            que.put('<h4>\t%d/%d Updating...</h4>' % (index + 1, _reasons_sql_data.__len__()))
            # Define data type.
            _version_new = list()
            summary = str()

            # Get jira.resources.Issue instance.
            _issue = self.jirahandler.read_issue(_reasons[2])
            # Get maxium version code from table reasons.
            _biggest_version = self.get_max_version(_reasons[0])[0]
            # Get issue existing versions.
            _ver_exists = _issue.fields.versions
            for key, ver in enumerate(_ver_exists):
                if _biggest_version == str(ver):
                    break
                # Set data once traverse to the list of the last one still can not 100% match.
                if -1 == key - len(_ver_exists):
                    # Issue have only one version.
                    if len(_ver_exists) == 1:
                        # Add new version to existing.
                        _version_new.append(str(ver))
                        _version_new.append(_biggest_version)
                        # Sort version by ASC.
                        _version_new.sort(key=lambda x: tuple(int(ver) for ver in x.split('.')))
                    # Replace the second version. This is biggest in the default.
                    else:
                        _version_new[-1] = _biggest_version
                    break
            # Get summary from JIRA issue.
            _exists_summary = _issue.fields.summary
            # Get Frequency from JIRA issue.
            frequency_regular_result = regular_common.frequency(_exists_summary)
            # Get Frequency integer data. Reasons might be have integer too.
            if not hasattr(frequency_regular_result, 'group'):      #返回true表示有匹配到
                LOG.cri(' %-20s ]-[ Issue %s did not have the keyword(frequency).' % (LOG.get_function_name(), _reasons[2]))
            else:
                _frequency_int = int(regular_common.interge(frequency_regular_result.group(0)).group(0))
                if _reasons[-1] != _frequency_int:
                    summary = regular_common.replace_frequency(_exists_summary, 'Frequency:%s' % _reasons[-1])
                    if _version_new or summary:
                        self.jirahandler.update_issue(_issue, _version_new, summary)
                    else:
                        LOG.info(' %-20s ]-[ Issue %s need not to update.' % (LOG.get_function_name(), _reasons[-2]))
        ReportGenerator.sum_tables()

    def submit_jira(self, que):
        """Submit issues to JIRA server.
        """
        # Get the reasons need to submit of today.
        _only_crash_id_l = self.match_reason()           #[{tableid:rowid}, ROWID, 1, CRASH_ID, PROJECT, REASON),()]
        if _only_crash_id_l.__len__() > 0:
            conn, cursor = sqlite_base.sqlite_connect()
            for index, _crash_id in enumerate(_only_crash_id_l):
                que.put('<h4>\t%d/%d Submitting...</h4>' % (index + 1, _only_crash_id_l.__len__()))
                # Get the log after parse from report table.
                _log_finally = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='PROJECT, VERSION, CALL, LOG',
                                                  table_name='report',
                                                  condition="where CRASH_ID = '%s'" % _crash_id[-3])
                if _log_finally:
                    _rowid = int()
                    # Transfer log data type to List.
                    _log_l = _log_finally[0][-1].split('\n')

                    # Get the first 7 lines of environment data to submit. Formart.
                    _env = '\n'.join(_log_l[1:7])

                    # Get version code.
                    _ver = _log_finally[0][1]
                    # Stitching the summary wait to submit.
                    _summary = 'Crash Analysis: ' + _log_finally[0][-2] + '[Frequency:%s]' % _crash_id[2]

                    # submit to JIRA server.
                    _jira_id = self.jirahandler.create(pjname=_log_finally[0][0],
                                                       summary=_summary,
                                                       environment=_env,
                                                       description=_log_finally[0][-1].replace('<pre>', '').replace(
                                                           '</pre>', ''),
                                                       version=_ver,
                                                       priority='urgen')

                    if isinstance(_jira_id, jira.resources.Issue):
                        # If ==, means submit success.
                        if regular_common.jira_id(_jira_id.key).group(0) == _jira_id.key:
                            # Insert data to reasons table.
                            _rowid = sqlite_base.insert(conn, cursor,
                                                        end=False,
                                                        table_name='reasons',
                                                        reason=_crash_id[-1],
                                                        frequency=_crash_id[2],
                                                        project=_log_finally[0][0],
                                                        jiraid=_jira_id.key)
                        else:
                            LOG.cri(' %-20s ]-[ Submit to JIRA error: %s .' % (LOG.get_function_name(), _jira_id.key))
                    else:
                        LOG.cri(' %-20s ]-[ Submit to JIRA error: %s .' % (LOG.get_function_name(), _jira_id))
                    # Treverse table id list.
                    for _tb_id in _crash_id[0].keys():
                        conditions = 'WHERE '
                        # Get row id list with given table id.
                        _row_l = _crash_id[0][_tb_id]
                        # Stitching the update condition command.
                        for key, _row_id in enumerate(_row_l):
                            if key >= 1:
                                conditions += ' or '
                            conditions += 'ROWID = %d' % _row_id
                        # Update reason id to backtrack tables.
                        sqlite_base.update(conn, cursor,
                                           end=False,
                                           table_name='backtrack_%s' % str(_tb_id),
                                           columns=['REASON_ID'],
                                           values=[_rowid],
                                           condition=conditions)

                else:
                    LOG.error(' %-20s ]-[ Table report cat not find CRASH_ID %s .' %
                              (LOG.get_function_name(), _crash_id[-2]))
            cursor.close()
            conn.close()
        else:
            LOG.info(' %-20s ]-[ Look like all crash has been logged: %s' %
                     (LOG.get_function_name(), ReportGenerator.get_yesterday_timestamp()))

    @staticmethod
    def sum_tables():
        """Log the data size of reasons and backtrack table(s).
        """
        conn = sqlite_base.sqlite_connect()
        cursor = conn[-1]
        # conn2, cursor2 = sqlite_base.sqlite_connect('Reasons.sqlite')
        _tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE TYPE=\'table\' AND name LIKE \'backtrack_%\'").fetchall()
        _num = int()
        for i in _tables:
            _num += int(cursor.execute("SELECT COUNT(*) FROM %s" % i).fetchall()[0][0])

        _reason = cursor.execute("SELECT SUM(FREQUENCY) FROM reasons").fetchall()[0][0]
        LOG.info(' %-20s ]-[ BACKTRACK ALL ITEM: %s , REASONS ALL ITEM: %s' % (LOG.get_function_name(), _num, _reason))
