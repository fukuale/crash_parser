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
    _reg = re.compile(r'[A-Z]+-\d*')
    return _reg.search(string_in)


def interge(str_in):
    """Regular for integer.

    Arguments:
        str_in {String} -- [The string need to filter.]
    """
    _reg = re.compile(r'\d+')
    return _reg.search(str_in)

def frequency(str_in):
    _reg = re.compile(r'Frequency\:[\d]+')
    return _reg.search(str_in)

def replace_frequency(str_in, new_str_in):
    return re.sub(r'Frequency\:[\d]+', new_str_in, str_in)

def crash_id(str_in):
    _reg = re.compile(r"if+\-\d+\-\d+")
    return _reg.search(str_in)
