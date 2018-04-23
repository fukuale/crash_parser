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

def version_number(str_in):
    _reg = re.compile(r'\d+(\.\d+){0,3}')
    return _reg.search(str_in)

def build_number_r(str_in):
    _reg = re.compile(r'[r]\d+')
    return _reg.search(str_in)

def consecutive_number(str_in):
    _reg = re.compile(r'[\d]{2,}')
    return _reg.search(str_in)

def chinese(str_in):
    _reg = re.compile(r'[\u4e00-\u9fa5]+')
    return _reg.search(str_in)