# Author = 'Vincent FUNG'
# Create = '2017/11/22'


class ParserException(Exception):
    def __init__(self, value):
        self.value = value


class ParseBaseInformationException(Exception):
    """
    Include version_information, product_name
    """
    def __init__(self, value):
        self.value = value


class ParseStacktraceInforException(Exception):
    def __init__(self, value):
        self.value = value


class ReadFromServerException(Exception):
    def __init__(self, value):
        self.value = value


class FailedToDownloadSYM(Exception):
    def __init__(self, value):
        self.value = value
