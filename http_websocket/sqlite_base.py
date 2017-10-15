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
import random
import time
import datetime
import sqlite3

import os


def get_today_timestamp(day=10):
    today = datetime.datetime.today() - datetime.timedelta(day) - datetime.timedelta(hours=4)
    return str(int(time.mktime(datetime.datetime(today.year, today.month, today.day, 0, 0, 0).timetuple())))


def sqlite_connect(sql_name='CrashCount.sqlite', sql_abs_path=0):
    """

    :return: Object sqlite Connection
    """
    sql_path = str()
    if not sql_abs_path:
        sql_path = os.path.join(os.path.expanduser('~'), 'CrashParser', 'database', sql_name)
    else:
        sql_path = sql_abs_path
    # conn = sqlite3.connect(':memory:')
    conn = sqlite3.connect(sql_path)
    if conn:
        print('crash_reason_count.db connected . . .')
        cursor = conn.cursor()
        if cursor:
            print('crash_reason_count.db opened . . .')
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
        (COUNT INT NOT NULL,
        CONTENT MESSAGE_TEXT NOT NULL,
        FIRST_VERSION MESSAGE_TEXT NOT NULL,
        LAST_VERSION MESSAGE_TEXT ,
        INSERT_TIME MESSAGE_TEXT NOT NULL,
        LAST_UPDATE MESSAGE_TEXT );''')
    print('table statistics create successfully . . .')
    if end:
        cursor.close()
        conn.close()


def create_backtrack_table(conn, cursor, end=True, **kwargs):
    """

    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Which id want to used to create the backtrack table. connect with statistics table's id.
    :return: Nothing to return
    """
    cursor.execute(
        'CREATE TABLE backtrack_%s(CRASH_ID MESSAGE_TEXT, REASON MESSAGE_TEXT, INSERT_TIME MESSAGE_TEXT NOT NULL,\
          LAST_UPDATE MESSAGE_TEXT );' % kwargs['id'])
    print('table of %s create successfully . . .' % kwargs['id'])
    if end:
        cursor.close()
        conn.close()


def create_report_table(conn, cursor, end=True, **kwargs):
    cursor.execute(
        'CREATE TABLE report(CRASH_ID MESSAGE_TEXT, LOG MESSAGE_TEXT);')
    print('report table create successfully . . .')
    if end:
        cursor.close()
        conn.close()


def create_reasons_table(conn, cursor, end=True, **kwargs):
    cursor.execute('CREATE TABLE reasons(REASON MESSAGE_TEXT, INSERT_TIME MESSAGE_TEXT NOT NULL)')
    if end:
        cursor.close()
        conn.close()


def create_unmatch_table(conn, cursor, end=True, **kwargs):
    cursor.execute('CREATE TABLE unmatch(CRASH_ID MESSAGE_TEXT, INSERT_TIME MESSAGE_TEXT NOT NULL)')
    if end:
        cursor.close()
        conn.close()


def create_tables(conn, cursor, tablename, end=True, create=True):
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

    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Included arg1: table_name, arg2: count, arg3:content, arg4:fv, arg5:lv, arg6:uptime
    :return:
    """
    print('insert kwargs', kwargs)
    inse = str()
    if create_tables(conn=conn, cursor=cursor, tablename=kwargs['table_name'], create=True, end=False):
        if kwargs['table_name'] == 'statistics':
            _inse_cmd_format = "INSERT INTO statistics(COUNT, CONTENT, FIRST_VERSION, LAST_VERSION, INSERT_TIME, LAST_UPDATE) values(?,?,?,?,?,?)"
            cursor.execute(_inse_cmd_format,
                           (kwargs['count'], kwargs['content'], kwargs['fv'], kwargs['lv'], get_today_timestamp(), get_today_timestamp()))

        elif kwargs['table_name'].startswith('backtrack_'):
            _inse_cmd_format_ = "INSERT INTO %s(CRASH_ID, INSERT_TIME) values(?,?)" % kwargs['table_name']
            print('inse_cmd_format', _inse_cmd_format_, kwargs['crash_id'])
            cursor.execute(_inse_cmd_format_, (kwargs['crash_id'], get_today_timestamp()))
        elif kwargs['table_name'] == 'report':
            _inse_cmd_format = "INSERT INTO report(CRASH_ID, LOG) values(?,?)"
            cursor.execute(_inse_cmd_format, (kwargs['crash_id'], kwargs['log']))
        elif kwargs['table_name'] == 'reasons':
            _inse_cmd_format = "INSERT INTO reasons(REASON, INSERT_TIME) VALUES(?,?)"
            cursor.execute(_inse_cmd_format, (kwargs['reason'], get_today_timestamp()))
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

    :param conn:
    :param cursor:
    :param end:
    :param kwargs:
    :return:
    """
    _update_sql = 'UPDATE %s SET ' % kwargs['table_name']
    print('kwargs****', kwargs)

    if 'columns' in kwargs.keys():
        for _index, _value in enumerate(kwargs['columns']):
            if _index >= 1:
                _update_sql += ', '
            if 'COUNT' == _value:
                _update_sql += 'COUNT = COUNT+1'
            else:
                _update_sql += "%s = \'%s\'" % (_value, kwargs['values'][_index])
        _update_sql += ", LAST_UPDATE = \'%s\' " % str(int(time.mktime(datetime.datetime.now().timetuple()))) + kwargs[
            'condition']

    elif 'reason' in kwargs.keys():
        _update_sql += "%s = \'%s\', LAST_UPDATE = \'%s\' %s" % ('REASON', kwargs['reason'], get_today_timestamp(), kwargs[
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


def search(conn, cursor, end=True, **kwargs):
    """

    :param end:
    :param conn: sqlite3 connection
    :param cursor: Object sqlite3
    :param kwargs: Included arg1: colum, arg2: table_name, arg3:condition(start with {where})
    :return: List type return. use index to get line's tuple. Then use index of the tuple to get aim data. OR BOOLEAN False.
    """

    try:
        search_sql = 'SELECT %s FROM %s %s' % (
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
        # TODO : WRITE LOG
        return False
