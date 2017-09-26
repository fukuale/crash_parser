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

import sqlite3


def sqlite_connect():
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
    cursor.execute('''CREATE TABLE statistics
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FIXED INT NOT NULL,
        COUNT INT NOT NULL,
        CONTENT TEXT NOT NULL,
        FIRST_VERSION TEXT NOT NULL,
        LAST_VERSION TEXT NOT NULL,
        LAST_UDPATE TEXT NOT NULL);''')
    print('table statistics create successfully . . .')
    if end:
        cursor.close()
        conn.close()


def create_backtrack(conn, cursor, end=True, **kwargs):
    cursor.execute(
        'CREATE TABLE backtrack_%d(ID INT PRIMARY KEY,TRAC_ID TEXT NOT NULL);' % id)
    # cursor.commit()
    print('table of %s create successfully . . .' % id)
    if end:
        cursor.close()
        conn.close()


def insert(conn, cursor, end=True, **kwargs):
    inse = "INSERT INTO %s VALUES(NULL, %d, %d, '%s', '%s', '%s', '%s')" % (
        kwargs['table_name'],
        kwargs['status'],
        kwargs['count'],
        kwargs['content'],
        kwargs['fv'],
        kwargs['lv'],
        kwargs['uptime'])
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
    print(cols)
    if cols > 1:
        for i in range(cols):
            if i == cols - 1:
                colums += ''.join([kwargs['colums'][i], '=', "\'", kwargs['volues'][i], "\'"])
                break
            colums += ''.join([kwargs['colums'][i], '=', "\'", kwargs['volues'][i], "\'", ', '])
        if kwargs['condition']:
            colums += kwargs['condition']

    udpate_sql = "UPDATE %s SET %s" % (
        kwargs['table_name'], colums)
    # print(udpate_sql)
    cursor.execute(udpate_sql)
    if end:
        cursor.close()
        conn.commit()
        conn.close()


def search(conn, cursor, end=True, **kwargs):
    """

    :param conn: sqlite3 connection
    :param cursor: Object sqlite3
    :param kwargs: Included arg1: colum, arg2: table_name, arg3:condition(start with {where})
    :return: Tuple type return. use index to get data.
    """
    search_sql = 'SELECT %s FROM %s %s' % (
        kwargs['colum'],
        kwargs['table_name'],
        kwargs['condition'])

    resu = cursor.execute(search_sql)
    print(resu.fetchall())
    if end:
        cursor.close()
        conn.close()


# create_backtrack(conn, 10)


conn, cursor = sqlite_connect()
print(type(conn), type(cursor))
create_base_table(conn, cursor, end=False)
for i in range(0, 3000):
    print(i)
    insert(
        end=False,
        conn=conn,
        cursor=cursor,
        status=0,
        count=i + 100,
        content='teoisjoiwejof',
        fv='first version',
        lv='last version',
        uptime=sqlite3.datetime.datetime.now(),
        table_name='statistics')
search(conn, cursor, False, colum='*', table_name='statistics', condition='where id = 2000')
cursor.close()
conn.commit()
conn.close()

# search(
#     cursor=cursor,
#     colum='*',
#     table_name='statistics',
#     condition='where ID = 201724')

# update(cursor, table_name='statistics',
#     colums=['COUNT',
#     'LAST_UDPATE',
#     'FIRST_VERSION'],
#     volues=['555555',
#     "update_date_2",
#     "first_version_udpate_2"],
#     condition='where id = 3')
