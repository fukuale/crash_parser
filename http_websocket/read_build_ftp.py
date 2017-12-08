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


class ReadVersionInfoFromFTP(object):
    def __init__(self):
        self.domain = 'http://10.0.2.188'
        self.wg = 'GameIM'
        self.sc = 'GameLive'
        self.platform = 'ios'
        self.appstore = 'AppStore正式发布'
        self.dSYM_published = 'AppStore正式发布/dsYM'
        self.dSYM_dev = 'dev/DSYM'

    def url_splicing(self, project):
        if project == 'GAMEIM':
            project = self.wg
        elif project == 'WELIVE':
            project = self.sc
        return os.path.join(self.domain, project, self.platform, self.appstore)

    def read_page(self, url):
        print('url: ' + url)
        url = parse.quote(url, safe='/:?=')
        return request.urlopen(url=url).read().decode('utf-8')

    def read_last_svn_code(self, project, jira_ver):
        """
        Return the last one build which was building for publish.
        :param project: This project name.
        :param jira_ver: Incoming max 3 versions.
        :return: String object. This is the newest build of published.
        """
        _pg_res = self.read_page(self.url_splicing(project=project)).split()
        _build = re.compile(r'[r]\d+')
        # reversed version list. Promote efficiency
        for ver in reversed(jira_ver):
            for index in range(1, _pg_res.__len__()):
                # Matching in reversed
                _res = _pg_res[index - 2 * index].find(ver)
                # Dismatch is -1.
                if _res > 0:
                    _b_code = _build.search(_pg_res[index - 2 * index])
                    return 'V%s (%s) [正式版]' % (ver, _b_code.group(0).replace('r', ''))

    def splicing_dsym_addr(self, project_name, type):
        _proj = str()
        _chl = str()
        if project_name == 'GAMEIM' or project_name == 'WeGamers':
            _proj = self.wg
        elif project_name == 'WELIVE' or project_name == 'StreamCraft':
            _proj = self.sc

        if type == 'appstore':
            _chl = self.dSYM_published
        elif type == 'dev':
            _chl = self.dSYM_dev

        return os.path.join(self.domain, _proj, self.platform, _chl)

    def read_dsym_dlink(self, project, type, build_num):
        _pg_res = self.read_page(self.splicing_dsym_addr(project_name=project, type=type))
        _pg_res = _pg_res.split('<td>')
        _file = re.compile('\".*?\"')
        for index in range(1, _pg_res.__len__()):
            _res = _pg_res[index - 2 * index].find(build_num)
            if _res > 0:
                _line = _pg_res[index - 2 * index]
                _f_name = _file.search(_line)
                return os.path.join(
                    self.splicing_dsym_addr(project_name=project, type=type),
                    _f_name.group(0).replace('"', '').replace('(', '\(').replace(')', '\)')
                )
