# Author = 'Vincent FUNG'
# Create = '2017/09/26'

import time
import datetime
import sqlite3

import os

# try:
from logger import Logger
# except ModuleNotFoundError:
#     from http_websocket.logger import Logger

LOG_FILE = os.path.join(os.path.expanduser(
    '~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'SQLiteBase')


def get_today_timestamp():
    """Get today timestamp.

    Returns:
        [String] -- [A timestamp.]
    """
    today = datetime.datetime.today() - datetime.timedelta(1)
    return str(int(time.mktime(
        datetime.datetime(
            today.year,
            today.month,
            today.day,
            today.hour,
            today.minute,
            today.second).timetuple()
    )))


def sqlite_connect(sql_name='CrashCount.sqlite', sql_abs_path=0):
    """Sqlite3 connector

    Keyword Arguments:
        sql_name {String} -- [Sqlite file name.] (default: {CrashCount.sqlite})
        sql_abs_path {String} -- [The sqlite file absolutely location.] (default: {0})

    Returns:
        Normally:
        [Sqlite3.Connection] -- [The sqlite conncetion.]
        False:
        [Boolean] -- [False]
    """
    if not sql_abs_path:
        sql_path = os.path.join(os.path.expanduser(
            '~'), 'CrashParser', 'database', sql_name)
    else:
        sql_path = sql_abs_path
    conn = sqlite3.connect(sql_path)
    if conn:
        cursor = conn.cursor()
        if cursor:
            return conn, cursor
        else:
            return False


def create_base_table(conn, cursor, end=True):
    """[summary]

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})

    Keyword Arguments:
        end {Boolean} -- [The signal to close or not] (default: {True})
    """
    cursor.execute('''CREATE TABLE statistics
        (FREQUENCY INT NOT NULL,
        CONTENT MESSAGE_TEXT NOT NULL,
        FIRST_VERSION MESSAGE_TEXT NOT NULL,
        LAST_VERSION MESSAGE_TEXT ,
        INSERT_TIME MESSAGE_TEXT NOT NULL,
        LAST_UPDATE MESSAGE_TEXT );''')
    if end:
        cursor.close()
        conn.close()


def create_backtrack_table(conn, cursor, end=True, **kwargs):
    """Create backtrack tables.

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        **kwargs {String} -- [Table id.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
    """
    cursor.execute('CREATE TABLE backtrack_%s( \
            CRASH_ID MESSAGE_TEXT, \
            REASON_ID MESSAGE_TEXT, \
            REASON MESSAGE_TEXT, \
            VERSION MESSAGE_TEXT, \
            INSERT_TIME MESSAGE_TEXT NOT NULL, \
            LAST_UPDATE MESSAGE_TEXT );' % kwargs['id'])
    if end:
        cursor.close()
        conn.close()


def create_report_table(conn, cursor, end=True):
    """Create report tabel.

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
    """
    cursor.execute(
        'CREATE TABLE report(CRASH_ID MESSAGE_TEXT, LOG MESSAGE_TEXT);')
    if end:
        cursor.close()
        conn.close()


def create_reasons_table(conn, cursor, end=True):
    """Create reasons table.

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
    """
    cursor.execute('''CREATE TABLE reasons(
        FIXED INT DEFAULT 0,
        JIRAID MESSAGE_TEXT,
        FREQUENCY INT DEFAULT 1,
        REASON MESSAGE_TEXT,
        INSERT_TIME MESSAGE_TEXT NOT NULL,
        LAST_UPDATE MESSAGE_TEXT)''')
    if end:
        cursor.close()
        conn.close()


def create_unmatch_table(conn, cursor, end=True):
    """Create unmatch table.

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
    """
    cursor.execute('''CREATE TABLE unmatch(
        CRASH_ID MESSAGE_TEXT,
        INSERT_TIME MESSAGE_TEXT NOT NULL)''')
    if end:
        cursor.close()
        conn.close()


def create_tables(conn, cursor, tablename, end=True, create=True):
    """[summary]

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        tablename {String} -- [What name want to create.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
        create {Boolean} -- [Create the table when this value set to True.] (default: {True})

    Returns:
        [Boolean] -- [If create successfully this will be True.]
    """
    exist = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % tablename
    if cursor.execute(exist).fetchall()[0][0] == 1:
        return True
    else:
        if create and tablename.startswith('backtrack_'):
            create_backtrack_table(conn, cursor, end=end,
                                   id=tablename.split('_')[-1])
            return True
        elif create and tablename == 'statistics':
            create_base_table(conn, cursor, end=end)
            return True
        elif create and tablename == 'report':
            create_report_table(conn, cursor, end=end)
            return True
        elif create and tablename == 'reasons':
            create_reasons_table(conn, cursor, end=end)
            return True
        elif create and tablename == 'unmatch':
            create_unmatch_table(conn, cursor, end=end)
            return True
        else:
            return False


def insert(conn, cursor, end=True, **kwargs):
    """[summary]

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        **kwargs {String} -- [What value want to insert.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})

    Returns:
        [Integer] -- [The line id just was inserted.]
    """
    inse = str()
    if create_tables(
            conn=conn, cursor=cursor, tablename=kwargs['table_name'], create=True, end=False):
        if kwargs['table_name'] == 'statistics':
            _inse_cmd_format = "INSERT INTO statistics(FREQUENCY, CONTENT, FIRST_VERSION, LAST_VERSION, INSERT_TIME, LAST_UPDATE) values(?,?,?,?,?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['frequency'], kwargs['content'], kwargs['fv'], kwargs['lv'], get_today_timestamp(),
                            get_today_timestamp()))

        elif kwargs['table_name'].startswith('backtrack_'):
            _inse_cmd_format_ = "INSERT INTO %s(CRASH_ID, VERSION,INSERT_TIME) values(?,?,?)" % kwargs[
                'table_name']
            cursor.execute(
                _inse_cmd_format_, (kwargs['crash_id'], kwargs['version'], get_today_timestamp()))
        elif kwargs['table_name'] == 'report':
            _inse_cmd_format = "INSERT INTO report(CRASH_ID, LOG) values(?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['crash_id'], kwargs['log']))
        elif kwargs['table_name'] == 'reasons':
            _inse_cmd_format = "INSERT INTO reasons(JIRAID, FREQUENCY, REASON, INSERT_TIME) VALUES(?,?,?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['jiraid'], kwargs['frequency'], kwargs['reason'], get_today_timestamp()))
        elif kwargs['table_name'] == 'unmatch':
            _inse_cmd_format = "INSERT INTO unmatch(CRASH_ID, INSERT_TIME) VALUES(?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['crash_id'], get_today_timestamp()))

    _row_id = cursor.execute('SELECT LAST_INSERT_ROWID()').fetchall()[0][0]
    cursor.execute(inse)
    conn.commit()
    if end:
        cursor.close()
        conn.commit()
        conn.close()

    return _row_id


def update(conn, cursor, end=True, **kwargs):
    """[summary]

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        **kwargs {String} -- [What value want to insert.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})

    Returns:
        [Integer] -- [The line id just was updated.]
    """
    _update_sql = 'UPDATE %s SET ' % kwargs['table_name']

    if 'columns' in kwargs.keys():
        for _index, _value in enumerate(kwargs['columns']):
            if _index >= 1:
                _update_sql += ', '
            if 'FREQUENCY' == _value:
                _update_sql += 'FREQUENCY = FREQUENCY+%s' % kwargs['values'][0]
            else:
                _update_sql += "%s = \'%s\'" % (_value,
                                                kwargs['values'][_index])
        _update_sql += ", LAST_UPDATE = \'%s\' " % get_today_timestamp() + kwargs[
            'condition']

    elif 'reason' in kwargs.keys():
        _update_sql += "%s = \'%s\', LAST_UPDATE = \'%s\' %s" % (
            'REASON', kwargs['reason'], get_today_timestamp(), kwargs[
                'condition'])

    cursor.execute(_update_sql)
    conn.commit()

    _row_id_update = search(conn, cursor,
                            end=False,
                            columns='rowid',
                            table_name=kwargs['table_name'],
                            condition=kwargs['condition'])

    if end:
        cursor.close()
        conn.close()
    return _row_id_update[0][0]


def search(conn, cursor, end=True, only=False, **kwargs):
    """[summary]

    Arguments:
        conn {Sqlite3.Connection} -- [The sqlite connection.]
        cursor {Sqlite3.Cusor} -- [The sqlite cursor.]
        **kwargs {String} -- [The search condition.]

    Keyword Arguments:
        end {Boolean} -- [Close the sqlite connection when this value set to True.] (default: {True})
        only {Boolean} -- [Search result the distinct data from sqlite when this value set to Ture.] (default: {False})

    Returns:
        Normally:
        [List] -- [The result of searching.]
        False:
        [Boolean] -- [When the sqlite3.OpeartioncalError was throw out.]
    """
    try:
        distinct = str()
        if only:
            distinct = 'DISTINCT '
        else:
            distinct = ''
        search_sql = 'SELECT %s %s FROM %s %s' % (
            distinct,
            kwargs['columns'],
            kwargs['table_name'],
            kwargs['condition'])
        result = cursor.execute(search_sql).fetchall()

        if end:
            cursor.close()
            conn.close()
            return result

        return result
    except sqlite3.OperationalError as sqlite_err:
        LOG.cri(' %-20s ]-[ SQLite search error %s' %
                (LOG.get_function_name(), sqlite_err))
        return False
