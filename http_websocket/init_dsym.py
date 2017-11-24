# -*- coding:utf-8 -*-
# Author = 'Vincent FUNG'
# Create = '2017/09/21'

import os

try:
    import subproc
    from parser_exception import ParserException
except ModuleNotFoundError as e:
    import http_websocket.subproc
    from http_websocket.parser_exception import ParserException

domain = 'http://10.0.2.188'
wegamers_folder = 'GameIM'
gamelive_folder = 'GameLive'
wegamer = 'WeGamers'
gamlive = 'GameLive'
appstore = 'AppStore正式发布/dsYM'
dev = 'dev/DSYM'
platform = 'ios'


class DownloadDSYM(object):
    def __init__(self):
        super(DownloadDSYM, self).__init__()
        self.proc = subproc.SubProcessBase()
        self.default_download_folder = os.path.join(
            os.path.expanduser('~'), 'CrashParser', 'dSYM')

    def init_dSYM(self, build_id, version_number, version_type, product):
        """
        Call all method to download dSYM file and rename after unzipping.
        :param build_id: String object. SVN code. eg.11311
        :param version_number: String object. eg.1.9.5
        :param version_type: String object. Application type, Default appstore
        :param product: String object. Product name, Default wegamers
        :return: String object. The dSYM absolute folder address.
        """
        _dSYM_name = '%s_%s.DSYM' % (product, build_id)
        _abs_dSYM = os.path.join(self.default_download_folder, _dSYM_name)
        # dSYM file already existing?
        if os.path.exists(_abs_dSYM):
            return _abs_dSYM  # return dSYM abspath

        else:
            # Call to get the download link
            http_addr = self.make_http_download_addr(build_id, version_number, version_type, product)
            if http_addr:
                download_cmd = 'curl -o %s %s' % (os.path.join(
                    self.default_download_folder, _abs_dSYM), http_addr)
                # Download file successfully.
                download_res = self.proc.sub_procs_run(cmd=download_cmd)
                if download_res:
                    # Valid files when the file size is more than 20MB
                    if os.path.getsize(os.path.join(os.path.join(
                            self.default_download_folder, _abs_dSYM))) > 20480:
                        unzip_zip_cmd = 'unzip -o %s -d %s' % (
                            os.path.join(self.default_download_folder, _abs_dSYM),
                            self.default_download_folder)
                        unzip_res = self.proc.sub_procs_run(cmd=unzip_zip_cmd)
                        # Unzip downloaded file successfully.
                        if unzip_res:
                            del_zip_cmd = 'rm -rf %s' % os.path.join(self.default_download_folder, _abs_dSYM)
                            # _abs_dSYM = self._abs_dSYM.replace('\\', '')
                            rm_temp_macosx = 'rm -rf %s' % os.path.join(self.default_download_folder, '__MACOSX/')
                            self.proc.sub_procs_run(cmd=del_zip_cmd)
                            self.proc.sub_procs_run(cmd=rm_temp_macosx)
                            grep_file = 'ls %s | grep %s.app' % (self.default_download_folder, product)
                            result = self.proc.sub_procs_run(cmd=grep_file).stdout.decode().split()[0]
                            os.rename(os.path.join(self.default_download_folder, result),
                                      _abs_dSYM)
                            return _abs_dSYM
        raise ParserException

    def make_http_download_addr(self, build_id, version_number, version_type='appsotre', product='wegamers'):
        """
        Splicing version and application type to call corresponding method get download address.
        :param build_id: String object. SVN code. eg.11311
        :param version_number: String object. eg.1.9.5
        :param version_type: String object. Default appstore
        :param product: String object. Default wegamers
        :return: getattr call corresponding method. The corresponding method return a download link.
        """
        method_name = '%s_%s' % (product.lower(), version_type)
        method = getattr(self, method_name)

        return method(build_id=build_id, version_number=version_number, version_type=version_type, product=product)

    def wegamers_appstore(self, **kwargs):
        """
        WeGamers AppStore dSYM download link maker
        :param kwargs: Accept build_id
        :return: String object. download link
        """
        _abs_dSYM = 'WeGamers.app.%s.dSYM.zip' % kwargs['build_id']
        return os.path.join(
            domain, wegamers_folder, platform, appstore, _abs_dSYM)

    def wegamers_hoc_dev(self, **kwargs):
        """
        WeGamers Develop dSYM download link maker
        :param kwargs: Accept 1)version_number, 2)build_id
        :return: String object. download link
        """
        _abs_dSYM = 'WeGamers_Enterprise_v%s\(r%s\).app.dSYM.zip' % (
            kwargs['version_number'], kwargs['build_id'])
        return os.path.join(
            domain, wegamers_folder, platform, dev, _abs_dSYM)

    def gamelive_appstore(self, build_id):
        """
        Not publish yet.
        :param build_id:
        :return:
        """
        pass

    def gamelive_hoc_dev(self, **kwargs):
        """
        GameLive Develop dSYM download link maker
        :param kwargs: Accept 1)version_number, 2)build_id
        :return: String object. download link
        """
        _abs_dSYM = 'GameLive_Enterprise_v%s\(r%s\).app.dSYM.zip' % (
            kwargs['version_number'], kwargs['build_id'])
        return os.path.join(
            domain, gamelive_folder, platform, dev, _abs_dSYM)
