# Author = 'Vincent FUNG'
# Create = '2018/01/09'

import re


def jira_id(string_in):
    """Regular for math JIRA_ID

    Arguments:
        string_in {String} -- [The id of jira issue.]

    Returns:
        [String] -- [Math result.]
    """
    _reg = re.compile(r'[A-Za-z]+-\d*')
    return _reg.search(string_in).group(0)


def interge(str_in):
    """Regular for integer.

    Arguments:
        str_in {String} -- [The string need to filter.]
    """
    _reg = re.compile(r'\d+')
    return _reg.search(str_in).group(0)
