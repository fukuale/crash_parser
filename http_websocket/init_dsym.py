# -*- coding:utf-8 -*-
# Author = 'Vincent FUNG'
# Create = '2017/09/21'

import os

from . import subproc
from .parser_exception import FailedToDownloadSYM
from .read_build_ftp import ReadVersionInfoFromFTP
import time


class DownloadDSYM(object):
    """Download dSYM file and return the absolute folder address.
    """
    def __init__(self):
        super(DownloadDSYM, self).__init__()
        self.proc = subproc.SubProcessBase()
        self.ftp = ReadVersionInfoFromFTP()
        self.default_download_folder = os.path.join(
            os.path.expanduser('~'), 'CrashParser', 'dSYM')

    def init_dsym(self, build_id, version_number, version_type, product_name, product_list):          ##解压后，目录下的StreamCraft文件, '4056','1.3.0','appstore'
        """Download dSYM file if not existing and return the absolute folder address.

        Arguments:
            build_id {String} -- [SVN code of this build.]
            version_number {String} -- [Version number of this build.]
            version_type {String} -- [AppStore build or develop build.]
            product_name {String} -- [Product name of this build.]

        Raises:
            FailedToDownloadSYM -- [The link parameters dismath version number.]
            FailedToDownloadSYM -- [Download failed.]

        Returns:
            [String] -- [The dSYM absolute folder address.]
        """
        _dsym_name = '%s_%s.DSYM' % (product_name, build_id)
        _abs_dsym = os.path.join(self.default_download_folder, _dsym_name)

        # dSYM file already existing?
        if os.path.exists(_abs_dsym):
            return _abs_dsym  # return dSYM abspath

        else:
            # Call to get the download link
            http_addr = self.get_http_download_addr(
                build_id=build_id,version_type=version_type, product_name=product_name, product_list=product_list)
            if http_addr:
                # Check the download is right with version number.
                if http_addr.find(build_id) > 0:
                    pass
                else:
                    raise FailedToDownloadSYM('The version number dismatch the download link!' + '\n' +
                                              'version: %s' % version_number + '\n' +
                                              'link: %s' % http_addr)
                # Splicing curl command.
                download_cmd = 'curl -o %s %s' % (os.path.join(self.default_download_folder, _abs_dsym), http_addr)
                # Download dSYM file.
                self.proc.sub_procs_run(cmd=download_cmd)
                # if download_res:
                # Valid files when the file size is more than 10MB
                if os.path.getsize(os.path.join(os.path.join(
                        self.default_download_folder, _abs_dsym))) > 102400:    #102400字节
                    unzip_zip_cmd = 'unzip -o %s -d %s' % (                      #将压缩文件test.zip在指定目录下解压缩，如果已有相同的文件存在，要求unzip命令覆盖原先的文件。
                        os.path.join(self.default_download_folder, _abs_dsym),   #解压DSYM.zip，过滤出解压后的*.app.DSYM文件夹,再重命名为_abs_dsym
                        self.default_download_folder)
                    unzip_res = self.proc.sub_procs_run(cmd=unzip_zip_cmd)
                    # Unzip downloaded file successfully.
                    if unzip_res:
                        # Splicing remove command.
                        del_zip_cmd = 'rm -rf %s' % os.path.join(self.default_download_folder, _abs_dsym)
                        rm_temp_macosx = 'rm -rf %s' % os.path.join(self.default_download_folder, '__MACOSX/')
                        # Remove useless file and folder after unzip dSYM file.
                        self.proc.sub_procs_run(cmd=del_zip_cmd)
                        self.proc.sub_procs_run(cmd=rm_temp_macosx)
                        # Get the unzipped file name.
                        grep_file = str()
                        # For StreamCraft.... The name is different with each place..
                        # if product_name == 'GameLive':
                        #     grep_file = 'ls %s | grep %s_AppStore.app' % (self.default_download_folder, product_name)
                        # else:
                        grep_file = "ls %s | grep -E '%s.app|%s_HOC.app|StreamCraft.app|SC'" % (self.default_download_folder, product_name, product_name)          #grep -E 匹配多个
                        result = self.proc.sub_procs_run(cmd=grep_file).stdout.decode().split()[0]
                        # Rename unzipped file.
                        os.rename(os.path.join(self.default_download_folder, result),
                                  _abs_dsym)
                        print(_abs_dsym)
                        time.sleep(3)
                        for dir in os.listdir(os.path.join(_abs_dsym,'Contents','Resources','DWARF')):
                            if 'SC' in dir:
                                os.rename(os.path.join(_abs_dsym,'Contents','Resources','DWARF',dir), os.path.join(_abs_dsym,'Contents','Resources','DWARF','StreamCraft'))
                        return _abs_dsym
        raise FailedToDownloadSYM('Maybe download dSYM file failed! Used link:%s' % http_addr)

    def get_http_download_addr(self, build_id, version_type, product_name, product_list):
        """Get http download address.

        Arguments:
            build_id {String} -- [The svn number of this build.]
            version_type {String} -- [AppStore build or develop build.]
            product_name {String} -- [Product name of this build.]

        Returns:
            [String] -- [The download link.]
        """
        return self.ftp.read_dsym_dlink(product_name=product_name, v_type=version_type, build_num=build_id, product_list=product_list)
