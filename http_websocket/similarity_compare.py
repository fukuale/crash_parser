# Author = 'Vincent FUNG'
# Create =  '2017/09/28'

try:
    import sqlite_base
except ModuleNotFoundError as e:
    from http_websocket import sqlite_base


class SimilarityCompute(object):
    def __init__(self, versioninfo, crashid):
        self.ver_info = versioninfo
        self.crash_id = crashid

    @staticmethod
    def hex_verify(contentin):
        try:
            int(contentin, 16)
        except ValueError as e:
            return False
        else:
            return True

    @staticmethod
    def compute_similarity(compare, be_compare):
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
        objectin = objectin.translate({ord(c): ' ' for c in '<>();!,.:+-[]_"'})
        _hex_rm = self.hex_remove(objectin)
        _re_str = ' '.join(_hex_rm)
        for i in _re_str:
            if not i.isdigit():
                _after += _after.join(i)
        return _after.split()

    def apple_locate_similarity(self, datain):
        # Parameters
        _first_match = list()
        _percent_of = list()  # 0)ID, 1)FREQUENCY, 2)CONTENT, 3)SIMILARITY PERCENT
        _row_id = int()

        # Connect to sql
        conn, cursor = sqlite_base.sqlite_connect()

        # Get wait compute data ready to match in sql.
        alpha_str = self.variable_remove(datain)
        for k, v in enumerate(alpha_str):
            if v.__len__() > 6:
                _first_match = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='ROWID, CONTENT',
                                                  table_name='statistics',
                                                  condition="where CONTENT LIKE \'%%%s%%\'" % v)
                break
        # Insert apple locate reason if not matched.
        if not _first_match:
            _row_id = sqlite_base.insert(conn, cursor,
                                         end=False,
                                         table_name='statistics',
                                         frequency=1,
                                         content=datain,
                                         fv=self.ver_info,
                                         lv=self.ver_info)
            # Insert backtrack information if statistics table inserted sucess.
            if _row_id:
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='backtrack_%d' % _row_id,
                                   crash_id=self.crash_id,
                                   version=self.ver_info)

        # Similarity compute logic
        if _first_match:
            for i in _first_match:

                # Remove be_compare string hex item.
                _sql_only_str = self.variable_remove(i[-1])

                # Compare two list similarity percentage.
                _percent_of.append((i[0], i[1], self.compute_similarity(alpha_str, _sql_only_str)))
            # Sorted by percentage.
            _percent_of = sorted(_percent_of, key=lambda x: (x[-1]))

        if _percent_of:
            # if 1 means 100% matched
            if 1 == _percent_of[-1][-1]:
                _row_id = sqlite_base.update(conn, cursor,
                                             end=False,
                                             table_name='statistics',
                                             columns=['FREQUENCY', 'LAST_VERSION'],
                                             values=[1, self.ver_info],  # count have to set one character.
                                             condition='where rowid = %d' % _percent_of[-1][0])
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='backtrack_%d' % _percent_of[-1][0],
                                   crash_id=self.crash_id,
                                   version=self.ver_info)
            else:
                _row_id = sqlite_base.insert(conn, cursor,
                                             end=False,
                                             table_name='statistics',
                                             frequency=1,
                                             content=datain,
                                             fv=self.ver_info,
                                             lv=self.ver_info)
                if _row_id:
                    sqlite_base.insert(conn, cursor,
                                       end=False,
                                       table_name='backtrack_%d' % _row_id,
                                       crash_id=self.crash_id,
                                       version=self.ver_info)
        if conn:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()
        return _row_id
