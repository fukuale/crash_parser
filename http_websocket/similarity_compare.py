# Author = 'Vincent FUNG'
# Create =  '2017/09/28'
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

try:
    import sqlite_base
except ModuleNotFoundError as e:
    from http_websocket import sqlite_base


class Smililarity_Compute(object):
    def __init__(self, datain, versioninfo, tracid):
        self.wait_compute_data = datain
        self.ver_info = versioninfo
        self.trac_id = tracid

    @staticmethod
    def hex_verify(contentin):
        try:
            int(contentin, 16)
        except ValueError as e:
            return False
        else:
            return True

    # @staticmethod
    # def get_standard_percentage(compare_list):
    #     if len(compare_list) < 10:
    #         return 0.7
    #     else:
    #         return 1

    def compute_similarity(self, compare, be_compare):
        """
        Compute two list object similarity percentage.
        :param compare: What list need to use for compare.
        :param be_compare: What list need to be compare.
        :return: float object
        """
        a = ''
        _re_compare = [a for i in compare if i in be_compare]
        _match_percent = float(len(_re_compare) / ((len(compare) + len(be_compare)) / 2))
        return _match_percent

    def hex_remove(self, objectin):
        """
        Remove hex from string or list. if type is string. Will be only split with space. not accept another character.
        :param objectin: String or list want to remove hex item.
        :return: two list type element. 1)_apple_reason_rehex 2)_sql_reason_rehex
        """
        if isinstance(objectin, list):
            return [x for x in objectin if not self.hex_verify(x)]
        else:
            return [x for x in objectin.split() if not self.hex_verify(x)]

    def variable_remove(self, objectin):
        """
        Remove hex and digital from string or list object. Base hex_remove()
        :param objectin: String or list want to remove.
        :return: List object.
        """
        _after = str()
        _hex_rm = self.hex_remove(objectin)
        _re_str = ' '.join(_hex_rm)
        for i in _re_str:
            if not i.isdigit():
                _after += _after.join(i)
        return _after.split()

    def similary_sql_op(self):
        # Parameters
        _first_match = list()
        _percent_of = list()  # 0)ID, 1)COUNT, 2)CONTENT, 3)SIMILARITY PERCENT

        # Connect to sql
        conn, cursor = sqlite_base.sqlite_connect()

        # Get wait compute data ready to match in sql.
        alpha_str = self.variable_remove(self.wait_compute_data)
        for k, v in enumerate(alpha_str):
            if v.__len__() > 3:
                _first_match = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='ROWID, COUNT, CONTENT',
                                                  table_name='statistics',
                                                  condition="where CONTENT LIKE \'%%%s%%\'" % alpha_str[0])

        if not _first_match:
            _row_id = sqlite_base.insert(conn, cursor,
                                         end=False,
                                         table_name='statistics',
                                         fixed=0,
                                         count=1,
                                         content=self.wait_compute_data,
                                         fv=self.ver_info,
                                         lv=self.ver_info)
            if _row_id:
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='backtrack_%d' % _row_id,
                                   trac_id=self.trac_id)

        # Similarity compute logic
        if _first_match:
            for i in _first_match:
                # Get what string will be comparation and split it.
                _target = i[-1].split()

                # Remove be_compare string hex item.
                _sql_only_str = self.variable_remove(_target)

                # Compare two list similarity percentage.
                _percent_of.append((i[0], i[1], i[2], self.compute_similarity(alpha_str, _sql_only_str)))
            # Sorted by percentage.
            _percent_of = sorted(_percent_of, key=lambda x: (x[-1]))
            print('_percent_of', _percent_of)

        if _percent_of:
            # if 1 means 100% matched
            if 1 == _percent_of[-1][-1]:
                sqlite_base.update(conn, cursor,
                                   end=False,
                                   table_name='statistics',
                                   columns=['COUNT', 'LAST_VERSION'],
                                   values=[_percent_of[-1][1] + 1, self.ver_info],
                                   condition='where ID = %d' % _percent_of[-1][0])
                print('100%')
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='backtrack_%d' % _percent_of[-1][0],
                                   trac_id=self.trac_id)
            else:
                _row_id = sqlite_base.insert(conn, cursor,
                                             end=False,
                                             table_name='statistics',
                                             fixed=0,
                                             count=1,
                                             content=self.wait_compute_data,
                                             fv=self.ver_info,
                                             lv=self.ver_info)
                print('percentage insert ', _row_id)
                if _row_id:
                    sqlite_base.insert(conn, cursor,
                                       end=False,
                                       table_name='backtrack_%d' % _row_id,
                                       trac_id=self.trac_id)
        if conn:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()


if __name__ == '__main__':
    data = "ERROR: All calls to UIKit need to happen on the main thread. You have a bug in your code. Use dispatch_async(dispatch_get_main_queue(), ^{ ... }); if you're unsure what thread you're in."
    sc = Smililarity_Compute(datain=data, versioninfo='1.9.3', tracid='656464533')
    sc.similary_sql_op()