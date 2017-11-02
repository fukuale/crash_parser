# Author = 'Vincent FUNG'
# Create = '2017/09/26'
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
import time
import datetime
import sqlite3

import os

try:
    from logger import Logger
except ModuleNotFoundError:
    from http_websocket.logger import Logger

log = Logger('/var/log/CrashParser.log', 'SQLiteBase')


def get_today_timestamp():
    today = datetime.datetime.today() - datetime.timedelta(1)
    return str(int(time.mktime(
        datetime.datetime(today.year, today.month, today.day, today.hour, today.minute, today.second).timetuple()
    )))


def sqlite_connect(sql_name='CrashCount.sqlite', sql_abs_path=0):
    """
    Connect to sqlite file. Default is CrashCount.sqlite
    :return: Object sqlite Connection
    """
    if not sql_abs_path:
        sql_path = os.path.join(os.path.expanduser('~'), 'CrashParser', 'database', sql_name)
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
    """
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :return: Nothing to return
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
    """
    Create backtrack tables.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Which id want to used to create the backtrack table. connect with statistics table's id.
    :return: Nothing to return
    """
    cursor.execute(
        'CREATE TABLE backtrack_%s(CRASH_ID MESSAGE_TEXT, REASON_ID MESSAGE_TEXT, REASON MESSAGE_TEXT, VERSION MESSAGE_TEXT, \
INSERT_TIME MESSAGE_TEXT NOT NULL, LAST_UPDATE MESSAGE_TEXT );' % kwargs['id'])
    if end:
        cursor.close()
        conn.close()


def create_report_table(conn, cursor, end=True):
    """
    Create report tables.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :return: Nothing to return
    """
    cursor.execute(
        'CREATE TABLE report(CRASH_ID MESSAGE_TEXT, LOG MESSAGE_TEXT);')
    if end:
        cursor.close()
        conn.close()


def create_reasons_table(conn, cursor, end=True):
    """
    Create reasons table.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :return: Nothing to return
    """
    cursor.execute('CREATE TABLE reasons(FIXED INT DEFAULT 0, JIRAID MESSAGE_TEXT, FREQUENCY INT DEFAULT 1,\
REASON MESSAGE_TEXT, INSERT_TIME MESSAGE_TEXT NOT NULL, LAST_UPDATE MESSAGE_TEXT)')
    if end:
        cursor.close()
        conn.close()


def create_unmatch_table(conn, cursor, end=True):
    """
    Create unmatch table.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :return: Nothing to return
    """
    cursor.execute('CREATE TABLE unmatch(CRASH_ID MESSAGE_TEXT, INSERT_TIME MESSAGE_TEXT NOT NULL)')
    if end:
        cursor.close()
        conn.close()


def create_tables(conn, cursor, tablename, end=True, create=True):
    """
    Create table call.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :return: True or False.
    """
    exist = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % tablename
    if cursor.execute(exist).fetchall()[0][0] == 1:
        return True
    else:
        if create and tablename.startswith('backtrack_'):
            create_backtrack_table(conn, cursor, end=end, id=tablename.split('_')[-1])
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
    """
    Insert data to tables.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Included arg1: table_name, arg2: count, arg3:content, arg4:fv, arg5:lv, arg6:uptime
    :return: Object int. rowid
    """
    inse = str()
    if create_tables(conn=conn, cursor=cursor, tablename=kwargs['table_name'], create=True, end=False):
        if kwargs['table_name'] == 'statistics':
            _inse_cmd_format = "INSERT INTO statistics(FREQUENCY, CONTENT, FIRST_VERSION, LAST_VERSION, INSERT_TIME, LAST_UPDATE) values(?,?,?,?,?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['frequency'], kwargs['content'], kwargs['fv'], kwargs['lv'], get_today_timestamp(),
                            get_today_timestamp()))

        elif kwargs['table_name'].startswith('backtrack_'):
            _inse_cmd_format_ = "INSERT INTO %s(CRASH_ID, VERSION,INSERT_TIME) values(?,?,?)" % kwargs['table_name']
            cursor.execute(_inse_cmd_format_, (kwargs['crash_id'], kwargs['version'], get_today_timestamp()))
        elif kwargs['table_name'] == 'report':
            _inse_cmd_format = "INSERT INTO report(CRASH_ID, LOG) values(?,?)"
            cursor.execute(_inse_cmd_format, (kwargs['crash_id'], kwargs['log']))
        elif kwargs['table_name'] == 'reasons':
            _inse_cmd_format = "INSERT INTO reasons(JIRAID, FREQUENCY, REASON, INSERT_TIME) VALUES(?,?,?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['jiraid'], kwargs['frequency'], kwargs['reason'], get_today_timestamp()))
        elif kwargs['table_name'] == 'unmatch':
            _inse_cmd_format = "INSERT INTO unmatch(CRASH_ID, INSERT_TIME) VALUES(?,?)"
            cursor.execute(_inse_cmd_format, (kwargs['crash_id'], get_today_timestamp()))

    _row_id = cursor.execute('SELECT LAST_INSERT_ROWID()').fetchall()[0][0]
    cursor.execute(inse)
    conn.commit()
    if end:
        cursor.close()
        conn.commit()
        conn.close()

    return _row_id


def update(conn, cursor, end=True, **kwargs):
    """
    Update data to tables.
    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Included arg1: table_name, arg2: columns, arg3:reason, arg4:condition
    :return: Object int. rowid
    """
    _update_sql = 'UPDATE %s SET ' % kwargs['table_name']

    if 'columns' in kwargs.keys():
        for _index, _value in enumerate(kwargs['columns']):
            if _index >= 1:
                _update_sql += ', '
            if 'FREQUENCY' == _value:
                _update_sql += 'FREQUENCY = FREQUENCY+%s' % kwargs['values'][0]
            else:
                _update_sql += "%s = \'%s\'" % (_value, kwargs['values'][_index])
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
    """
    Search data from tables.
    :param only: DISTINCT option. If True. Will return the only data.
    :param conn: sqlite3 connection
    :param cursor: Object sqlite3
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Included arg1: colum, arg2: table_name, arg3:condition(start with {where})
    :return: List type return. use index to get line's tuple. Then use index of the tuple to get aim data. OR BOOLEAN False.
    """

    try:
        distinct = str()
        if only:
            distinct = 'DISTINCT '
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
    except sqlite3.OperationalError as e:
        log.cri(' %-20s ]-[ SQLite search error %s' % (log.get_function_name(), e))
        return False
