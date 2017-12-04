# Author = 'Vincent FUNG'
# Create = '2017/12/04'

from urllib import request
from urllib import parse

import os

import re

try:
    pass
except ModuleNotFoundError:
    pass


class ReadLastBuildFromServer(object):
    def __init__(self):
        self.domain = 'http://10.0.2.188'
        self.wg = 'GameIM'
        self.sc = 'GameLive'
        self.appstore = 'ios/AppStore正式发布'

    def url_splicing(self, project):
        if project == 'GAMEIM':
            project = self.wg
        elif project == 'WELIVE':
            project = self.sc
        return os.path.join(self.domain, project, self.appstore)

    def read_page(self, project):
        url = parse.quote(self.url_splicing(project=project), safe='/:?=')
        return request.urlopen(url=url).read().decode('utf-8')

    def read_last_svn_code(self, project, jira_ver):
        _pg_res = self.read_page(project=project).split()
        _build = re.compile(r'[r]\d+')
        _temp_last = int()
        for ver in reversed(jira_ver):
            for index in range(1, _pg_res.__len__()):
                _res = _pg_res[index - 2 * index].find(ver)
                if _res > 0:
                    _temp_last = index
                    break
            if _temp_last:
                _b_code = _build.search(_pg_res[_temp_last - 2 * _temp_last])

                return 'V%s (%s) [正式版]' % (ver, _b_code.group(0).replace('r', ''))


if __name__ == '__main__':
    da = ('1.9.6', '1.9.7', '2.0.0', '2.0.1', '2.0.2')
    rl = ReadLastBuildFromServer()
    print(rl.read_last_svn_code(project='GAMEIM', jira_ver=da))
