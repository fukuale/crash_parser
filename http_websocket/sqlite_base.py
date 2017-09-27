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


def sqlite_connect():
    """

    :return: Object sqlite Connection
    """
    conn = sqlite3.connect(':memory:')
    # conn = sqlite3.connect('db/crash_reason_count.sqlite')
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
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FIXED INT NOT NULL,
        COUNT INT NOT NULL,
        CONTENT TEXT NOT NULL,
        FIRST_VERSION TEXT NOT NULL,
        LAST_VERSION TEXT,
        LAST_UPDATE TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP));''')
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
        'CREATE TABLE backtrack_%d(ID INT PRIMARY KEY,TRAC_ID TEXT NOT NULL);' % id)
    # cursor.commit()
    print('table of %s create successfully . . .' % id)
    if end:
        cursor.close()
        conn.close()


def insert(conn, cursor, end=True, **kwargs):
    """

    :param conn: Object sqlite Connection
    :param cursor: Object sqlite Cursor
    :param end: Boolean type, if True will be close sqlite connect after this method.
    :param kwargs: Included arg1: table_name, arg2: count, arg3:content, arg4:fv, arg5:lv, arg6:uptime
    :return:
    """
    inse = "INSERT INTO %s VALUES(NULL, %d, %d, '%s', '%s', '%s'," \
           "str(int(time.mktime(datetime.datetime.now().timetuple()))))" % (
        kwargs['table_name'],
        kwargs['fixed'],
        kwargs['count'],
        kwargs['content'],
        kwargs['fv'],
        kwargs['lv'])
    cursor.execute(inse)

    if end:
        cursor.close()
        conn.commit()
        conn.close()


def update(conn, cursor, end=True, **kwargs):
    """

    :param conn:
    :param cursor:
    :param end:
    :param kwargs:
    :return:
    """
    colums = ''
    cols = len(kwargs['colums'])
    if cols > 1:
        for i in range(cols):
            colums += ''.join([kwargs['colums'][i], '=', "\'", kwargs['values'][i], "\'", ', '])
        colums += ''.join(['LAST_UPDATE', '=', "\'", str(int(time.mktime(datetime.datetime.now().timetuple()))), "\'"])
        if kwargs['condition']:
            colums += kwargs['condition']

    udpate_sql = "UPDATE %s SET %s" % (
        kwargs['table_name'], colums)
    cursor.execute(udpate_sql)

    if end:
        cursor.close()
        conn.commit()
        conn.close()


def search(conn, cursor, end=True, **kwargs):
    """

    :param end:
    :param conn: sqlite3 connection
    :param cursor: Object sqlite3
    :param kwargs: Included arg1: colum, arg2: table_name, arg3:condition(start with {where})
    :return: List type return. use index to get line's tuple. Then use index of the tuple to get aim data.
    """
    search_sql = 'SELECT %s FROM %s %s' % (
        kwargs['colums'],
        kwargs['table_name'],
        kwargs['condition'])

    result = cursor.execute(search_sql).fetchall()

    if end:
        cursor.close()
        conn.close()
        return result

    return result


def random_c():
    contents = {
        1: 'IOWJhdfthtyjtrukjfgnFWF',
        2: 'OBIWErtsrjtyjgesrgertsegthJQKWF',
        3: 'OOQWFrthdrtWEF6845ADFG',
        4: 'OUIBPWthhgrynwegfeOEQORJ',
        5: 'JXCVPOawefhrthQEWF',
        6: 'jaUWENcfawefagnFIAWE',
        7: '6546AWdfgncfghndfghE1F35',
        8: 'IOVJAWOEKFawerfgawefNALWF3',
        9: '126B54cgndrthsertghdfSER',
        10: '68465ghdfghfg45416',
        11: 'oaiwejfjndfghdrtoi651',
        12: 'wejfoi6WFEGG',
        13: 'oaiwejfoi651'
    }

    re = random.randint(1, 13)

    return contents[re]

# create_backtrack_table(conn, 10)


conn, cursor = sqlite_connect()
print(type(conn), type(cursor))
create_base_table(conn, cursor, end=False)
for i in range(0, 600):
    # print(i)
    insert(
        end=False,
        conn=conn,
        cursor=cursor,
        status=0,
        count=i + 100,
        content=random_c(),
        fv='first version',
        lv='last version',
        table_name='statistics')

update(conn, cursor, end=False, table_name='statistics', colums=['COUNT', 'CONTENT'], values=['100', 'test'], condition='where id = 10')

_unknow_type = 'EKFawerfgaw'
cond = "where CONTENT LIKE \'%%%s%%\'" % _unknow_type
_target = search(conn,
                 cursor,
                 end=False,
                 colums='ID, CONTENT',
                 table_name='statistics',
                 condition=cond)
print('target ', _target)

cursor.close()
conn.commit()
conn.close()
