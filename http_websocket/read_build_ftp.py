# Author = 'Vincent FUNG'
# Create = '2017/12/04'
import os
import re
from urllib import parse, request

from parser_exception import ReadFromServerException


class ReadVersionInfoFromFTP(object):
    """Read version information from FTP server.
    """
    def __init__(self):
        self.domain = 'http://10.0.2.188'
        self.platform = 'ios'
        self.appstore = 'AppStore正式发布'
        self.dsym_published = 'AppStore正式发布/dsYM'
        self.dsym_dev = 'dev/DSYM'

    def url_stitching(self, project_name):
        """Url stitching.

        Arguments:
            project_name {List} -- [Project name.]

        Returns:
            [String] -- [Full url address.]
        """
        return os.path.join(self.domain, project_name, self.platform, self.appstore)

    def read_page(self, url):
        """Read FTP page.

        Arguments:
            url {String} -- [FTP address.]

        Returns:
            [String] -- [Page content.]
        """
        if 'WELIVE' in url and url.startswith('http://10.0.2.188'):
            url = url.replace('WELIVE', 'GAMELIVE')
        url = parse.quote(url, safe='/:?=')
        try:
            return request.urlopen(url=url).read().decode('utf-8')
        except request.HTTPError as http_err:
            raise ReadFromServerException('%s(%s)' % (http_err, url))

    def stitching_last_version(self, project_name, jira_ver):
        """Get the version code of last build.

        Arguments:
            project_name {String} -- [The name of project.]
            jira_ver {List} -- [The versions of this project.]
        """
        _pg_res = self.read_page(self.url_stitching(project_name=project_name)).split()
        _build = re.compile(r'[r]\d+')
        # reversed version list. Promote efficiency
        for ver in reversed(jira_ver):
            for index in range(1, _pg_res.__len__()):
                # Matching in reversed
                _res = _pg_res[0 - index].find(ver)
                if _res > 0:
                    _b_code = _build.search(_pg_res[0 - index])
                    return 'V%s (%s) [正式版]' % (ver, _b_code.group(0).replace('r', ''))

    def dsym_addr_stithing(self, project_name, v_type, pj_list):
        """[summary]

        Arguments:
            project_name {[type]} -- [description]
            type {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        _proj = str()
        _chl = str()
        # FIXME: pj_list IS A LIST WHEN CALL BY SPECIAL CRASH_ID.
        if isinstance(pj_list, dict):
            for pj_key in pj_list.keys():
                if project_name == pj_list[pj_key]:
                    _proj = pj_key
                elif project_name == 'GameLive':
                    _proj = project_name
        else:
            for pj_key in pj_list:
                if project_name == pj_key:
                    _proj = pj_key
                elif project_name == 'GameLive':
                    _proj = project_name

        if v_type == 'appstore':
            _chl = self.dsym_published
        elif v_type == 'dev':
            _chl = self.dsym_dev

        return os.path.join(self.domain, _proj, self.platform, _chl)

    def read_dsym_dlink(self, product_name, v_type, build_num, product_list):
        """[summary]

        Arguments:
            project {[type]} -- [description]
            type {[type]} -- [description]
            build_num {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        _pg_res = self.read_page(self.dsym_addr_stithing(project_name=product_name, v_type=v_type, pj_list=product_list))
        _pg_res = _pg_res.split('<tr>')
        _file = re.compile(r"[\w\_]*\.[\w]*\.[0-9].*\.zip")
        for index in range(1, _pg_res.__len__()):
            _res = _pg_res[0 - index].find(build_num)
            if _res > 0:
                _line = _pg_res[0 - index]
                _f_name = _file.search(_line)
                return os.path.join(
                    self.dsym_addr_stithing(project_name=product_name, v_type=v_type, pj_list=product_list),
                    _f_name.group(0).replace('(', r'\(').replace(')', r'\)')
                )
        else:
            raise ReadFromServerException("Can not get the file name from dSYM FTP with build version(%s)" % build_num)
