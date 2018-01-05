# -*- coding:utf-8 -*-
# Author = 'Vincent FUNG'
# Create = '2017/09/21'

import os

# try:
import subproc
from parser_exception import FailedToDownloadSYM
from read_build_ftp import ReadVersionInfoFromFTP
# except ModuleNotFoundError as e:
#     import http_websocket.subproc
#     from http_websocket.parser_exception import FailedToDownloadSYM
#     from http_websocket.read_build_ftp import ReadVersionInfoFromFTP

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
        self.ftp = ReadVersionInfoFromFTP()
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
            http_addr = self.get_http_download_addr(build_id, version_type, product)
            if http_addr:
                # Check the download is right with version number.
                if http_addr.find(build_id) > 0:
                    pass
                else:
                    raise FailedToDownloadSYM('The version number dismatch the download link!' + '\n' +
                                              'version: %s' % version_number + '\n' +
                                              'link: %s' % http_addr)
                # Splicing curl command.
                download_cmd = 'curl -o %s %s' % (os.path.join(self.default_download_folder, _abs_dSYM), http_addr)
                # Download dSYM file.
                self.proc.sub_procs_run(cmd=download_cmd)
                # if download_res:
                # Valid files when the file size is more than 10MB
                if os.path.getsize(os.path.join(os.path.join(
                        self.default_download_folder, _abs_dSYM))) > 102400:
                    unzip_zip_cmd = 'unzip -o %s -d %s' % (
                        os.path.join(self.default_download_folder, _abs_dSYM),
                        self.default_download_folder)
                    unzip_res = self.proc.sub_procs_run(cmd=unzip_zip_cmd)
                    # Unzip downloaded file successfully.
                    if unzip_res:
                        # Splicing remove command.
                        del_zip_cmd = 'rm -rf %s' % os.path.join(self.default_download_folder, _abs_dSYM)
                        rm_temp_macosx = 'rm -rf %s' % os.path.join(self.default_download_folder, '__MACOSX/')
                        # Remove useless file and folder after unzip dSYM file.
                        self.proc.sub_procs_run(cmd=del_zip_cmd)
                        self.proc.sub_procs_run(cmd=rm_temp_macosx)
                        # Get the unzipped file name.
                        grep_file = 'ls %s | grep %s.app' % (self.default_download_folder, product)
                        result = self.proc.sub_procs_run(cmd=grep_file).stdout.decode().split()[0]
                        # Rename unzipped file.
                        os.rename(os.path.join(self.default_download_folder, result),
                                  _abs_dSYM)
                        return _abs_dSYM
        raise FailedToDownloadSYM('Maybe download dSYM file failed! Used link:%s' % http_addr)

    def get_http_download_addr(self, build_id, version_type='appsotre', product='wegamers'):
        """
        Call ftp to get splicing download link for dSYM file.
        :param build_id: Application svn code used for build. The only id.
        :param version_type: Application type.
        :param product: What name of the application.
        :return: String object. The download link.
        """
        return self.ftp.read_dsym_dlink(project=product, type=version_type, build_num=build_id)
