# -*- coding:utf-8 -*-
# Author = 'Vincent FUNG'
# Create = '2017/09/21'
#                       ::
#                      :;J7, :,                        ::;7:
#                      ,ivYi, ,                       ;LLLFS:
#                      :iv7Yi                       :7ri;j5PL
#                     ,:ivYLvr                    ,ivrrirrY2X,
#                     :;r;j5P.7r:                :ivuksxerfnli.
#                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur
#                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17
#                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i
#              :,, ,,:   ,::irii:i:::.irii:i:::j1jri7ZBOS7ivv,
#                 ,::,    ::rv77iiiriii:iii:i::,rvLrYXqZEk.Li
#             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:
#           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri
#          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:
#        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::
#        :      iuMMP: :,:::,:ii;Y#LYBB0viiii:i:iii:i:::iJqL;::
#       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii
#      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:
#     ,               ,,,,::::i:  :i:i:i:i.       ,:,, ,:::ii;i7:
#    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii
#    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::
#    i,  ,  ,8@VINCENTBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::
#    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,
#    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:
#    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::
#    :     :rkwwiBivf.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,
#     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:ia5wf88s5.,
#          , :r50EZ8MILOVEYOUBZP7::::i::,:::::,: :,:,::i;rrririiii::
#              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
#           ,:  :::,: :,,:,,,::::i:i:::::::::::,,:::::iir;ii;7v7;ii;i,
#           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiii;L8OGJrf.r;7:i,
#        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
#         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;:::i:::i:ii:::
#                          _
#                      o _|_           __
#                      |  |      (__| (__) (__(_
#                                   |

import os, time

try:
    import subproc
except ModuleNotFoundError as e:
    import http_websocket.subproc

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
        Call all method to download dSYM file and rename it after unzipping.
        :param build_id: String object. SVN code. eg.11311
        :param version_number: String object. eg.1.9.5
        :param version_type: String object. Default appstore
        :param product: String object. Default wegamers
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
                        unzip_zip_cmd = 'unzip %s -d %s' % (
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
                            test1 = os.path.join(self.default_download_folder, result)
                            test2 = _abs_dSYM
                            os.rename(os.path.join(self.default_download_folder, result),
                                      _abs_dSYM)
                            return _abs_dSYM
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False

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
        print(method_name)
        method = getattr(self, method_name)

        return method(build_id=build_id, version_number=version_number, version_type=version_type, product=product)

    def wegamers_appstore(self, **kwargs):
        """
        WeGamers AppStore dSYM download link maker
        :param kwargs: Accept build_id
        :return: String object. download link
        """
        self._abs_dSYM = 'WeGamers.app.%s.dSYM.zip' % kwargs['build_id']
        return os.path.join(
            domain, wegamers_folder, platform, appstore, self._abs_dSYM)

    def wegamers_dev(self, **kwargs):
        """
        WeGamers Develop dSYM download link maker
        :param kwargs: Accept 1)version_number, 2)build_id
        :return: String object. download link
        """
        print(kwargs)
        self._abs_dSYM = 'WeGamers_Enterprise_v%s\(r%s\)-dSYM.zip' % (
            kwargs['version_number'], kwargs['build_id'])
        return os.path.join(
            domain, wegamers_folder, platform, dev, self._abs_dSYM)

    def gamelive_appstore(self, build_id):
        """
        Not publish yet.
        :param build_id:
        :return:
        """
        pass

    def gamelive_dev(self, **kwargs):
        """
        GameLive Develop dSYM download link maker
        :param kwargs: Accept 1)version_number, 2)build_id
        :return: String object. download link
        """
        self._abs_dSYM = 'GameLive_Enterprise_v%s\(r%s\)-dSYM.zip' % (
            kwargs['version_number'], kwargs['build_id'])
        return os.path.join(
            domain, gamelive_folder, platform, dev, self._abs_dSYM)
