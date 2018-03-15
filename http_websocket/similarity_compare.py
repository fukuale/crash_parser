# Author = 'Vincent FUNG'
# Create =  '2017/09/28'

import sqlite_base


class SimilarityCompute(object):
    """Compute two data similarity to return a precentage of it.
    """
    def __init__(self, versioninfo, crashid):
        self.ver_info = versioninfo
        self.crash_id = crashid

    @staticmethod
    def hex_verify(contentin):
        """Verify content is hex data or not.

        Arguments:
            contentin {String} -- [The data waiting for verification.]

        Returns:
            [Boolean] -- [Boolean type. True)HEX data. False)Isn't]
        """
        try:
            int(contentin, 16)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def compute_similarity(compare, be_compare):
        """Similarity compute.

        Arguments:
            compare {String} -- [One of the data need to compute.]
            be_compare {String} -- [Other one data need to compute.]

        Returns:
            [Float] -- [Similarity percentage.]
        """
        _matched = ''
        _re_compare = [_matched for i in compare if i in be_compare]
        _match_percent = float(len(_re_compare) / ((len(compare) + len(be_compare)) / 2))
        return _match_percent

    def hex_remove(self, objectin):
        """Remove hex from object.

        Arguments:
            objectin {String/List} -- [String or list want to remove hex item.]

        Returns:
            [List] -- [List without hex items.]
        """
        if isinstance(objectin, list):
            return [x for x in objectin if not self.hex_verify(x)]
        else:
            return [x for x in objectin.split() if not self.hex_verify(x)]

    def mutable_remove(self, objectin):
        """Remove mutable data and symbol from object.

        Arguments:
            objectin {String} -- [description]

        Returns:
            [List] -- [List with immutable items.]
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
        """Compute similarity of apple located reason.

        Arguments:
            datain {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        # Parameters
        _first_match = list()
        _percent_of = list()  # 0)ID, 1)FREQUENCY, 2)CONTENT, 3)SIMILARITY PERCENT
        _row_id = int()

        # Connect to sql
        conn, cursor = sqlite_base.sqlite_connect()

        # Use the specific keyword to get as little data as possible from sqlite.
        alpha_str = self.mutable_remove(datain)
        for chars in alpha_str:
            # 6, Lenght of the keyword. Reduce the probability of duplication.
            if chars.__len__() > 6:
                _first_match = sqlite_base.search(conn, cursor,
                                                  end=False,
                                                  columns='ROWID, FREQUENCY, CONTENT',
                                                  table_name='statistics',
                                                  condition="where CONTENT LIKE \'%%%s%%\'" % chars)
                break
        # Insert apple located reason if not matched.
        if not _first_match:
            _row_id = sqlite_base.insert(conn, cursor,
                                         end=False,
                                         table_name='statistics',
                                         frequency=1,
                                         content=datain,
                                         fv=self.ver_info,
                                         lv=self.ver_info)
            # Insert backtrack information when statistics table insertion sucess.
            if _row_id:
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   table_name='backtrack_%d' % _row_id,
                                   crash_id=self.crash_id,
                                   version=self.ver_info)

        # Similarity compute logic.
        if _first_match:
            for _item in _first_match:

                # Clean string.
                _sql_only_str = self.mutable_remove(_item[-1])

                # Compare the percentage of similarity. item[0]=ROWID, item[1]=CONTENT.
                _percent_of.append(
                    (_item[0], _item[1], self.compute_similarity(alpha_str, _sql_only_str))
                    )
            # Sort percentage by ASC. (0.1 .. 1)
            _percent_of = sorted(_percent_of, key=lambda x: (x[-1]))

        if _percent_of.__len__() != 0:
            # number 1 means 100% matched.
            if _percent_of[-1][-1] == 1:
                _row_id = sqlite_base.update(conn, cursor,
                                             end=False,
                                             table_name='statistics',
                                             columns=['FREQUENCY', 'LAST_VERSION'],
                                             values=[_item[1] + 1, self.ver_info],  # count have to set one character.
                                             condition='where rowid = %d' % _percent_of[-1][0])
                sqlite_base.insert(conn, cursor,
                                   end=False,
                                   # table statistics rowid == backtrack table id.
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
