# Author = 'Vincent FUNG'
# Create = '2017/09/20'
'''
                       ::
                      :;J7, :,                        ::;7:
                      ,ivYi, ,                       ;LLLFS:
                      :iv7Yi                       :7ri;j5PL
                     ,:ivYLvr                    ,ivrrirrY2X,
                     :;r@Wwz.7r:                :ivu@kexianli.
                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur
                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17
                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i
              :,, ,,:   ,:# Author = 'Vincent FUNG'BOS7ivv,
                 ,::,    :# Create = '2017/09/20'Lq@huhao.Li
             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:
           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri
          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:
        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::
        :      iuMMP: :,:::,:ii;2GY7OBB0viiii:i:iii:i:::iJqL;::
       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii
      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:
     ,               ,,,,::::i:  @arqiao.       ,:,, ,:::ii;i7:
    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii
    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::
    i,  ,  ,8BMMBBBBBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::
    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,
    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:
    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::
    :     :rk@Yizero.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,
     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:i@petermu.,
          , :r50EZ8MBBBBGOBBBZP7::::i::,:::::,: :,:,::i;rrririiii::
              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
           ,:  :@kevensun.:,:,,,::::i:i:::::,,::::::iir;ii;7v77;ii;i,
           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiir@xingjief.r;7:i,
        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;@Secbone.ii:::

'''

# cmd = atos -arch arm64 -o /Users/vincent.fung/Downloads/WeGamers.app.11311.dSYM/Contents/Resources/DWARF/WeGamers -l 0x00000001000f0000  0x00000001001338ec


byts = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: 841504ae-b029-487c-ade7-394769d59e2b\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 4470\r\nConnection: keep-alive\r\n\r\n{"data":"=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\r\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\r\ndeviceType:         iPhone 6\r\nIOS Ver:            iPhone OS 8.3\r\navailableMemory:    83.5MB\r\nusedMemory:         66.7MB\r\ntime:               2017-09-17_15-11-54\r\nnUid:               0\r\nsName:              \r\nsLinkID:            \r\nsBindEmail:         \r\nphone:              \r\n\r\nERROR: All calls to UIKit need to happen on the main thread. You have a bug in your code. Use dispatch_async(dispatch_get_main_queue(), ^{ ... }); if you\'re unsure what thread you\'re in.\r\n\r\nBreak on PSPDFAssertIfNotMainThread to find out where.\r\n\r\nStacktrace: (\r\n\t0   WeGamers                            0x0000000100b84f70 WeGamers + 11226992\r\n\t1   WeGamers                            0x0000000100b84ff0 WeGamers + 11227120\r\n\t2   UIKit                               0x00000001891004ac  + 160\r\n\t3   MediaPlayer                         0x00000001865b3874  + 1108\r\n\t4   MediaPlayer                         0x00000001865b1fa8  + 240\r\n\t5   MediaPlayer                         0x00000001865b2034  + 88\r\n\t6   WebCore                             0x000000019351951c  + 192\r\n\t7   WebCore                             0x00000001935197f8  + 468\r\n\t8   WebCore                             0x0000000193518bf8  + 96\r\n\t9   WebCore                             0x0000000193518b68 _ZN7WebCore19MediaSessionManager13sharedManagerEv + 56\r\n\t10  WebCore                             0x000000019351766c  + 44\r\n\t11  WebCore                             0x000000019305733c  + 36\r\n\t12  WebCore                             0x000000019303fc34  + 1100\r\n\t13  WebCore                             0x00000001930169a4  + 64\r\n\t14  WebCore                             0x000000019302b794  + 92\r\n\t15  WebCore                             0x000000019302b554  + 336\r\n\t16  WebCore                             0x0000000192b7bf38  + 164\r\n\t17  WebCore                             0x0000000192b7bd18  + 36\r\n\t18  WebCore                             0x0000000192b7a61c  + 1924\r\n\t19  WebCore                             0x0000000192b79048  + 2496\r\n\t20  WebCore                             0x0000000192b78594  + 136\r\n\t21  WebCore                             0x0000000192b78440  + 312\r\n\t22  WebCore                             0x0000000192b77c68  + 140\r\n\t23  WebCore                             0x0000000192b61f20  + 384\r\n\t24  WebCore                             0x0000000192bcac68  + 428\r\n\t25  WebCore                             0x0000000192e785ac  + 116\r\n\t26  WebCore                             0x0000000192b93bf0 _ZN7WebCore14DocumentLoader10commitDataEPKcm + 64\r\n\t27  WebKitLegacy                        0x0000000193a2bdb8  + 140\r\n\t28  WebKitLegacy                        0x0000000193a2bcac  + 76\r\n\t29  WebKitLegacy                        0x0000000193a2bc40  + 124\r\n\t30  WebCore                             0x0000000192bc0bf8  + 164\r\n\t31  WebCore                             0x0000000192bc0a80 _ZN7WebCore14DocumentLoader12dataReceivedEPNS_14CachedResourceEPKci + 348\r\n\t32  WebCore                             0x0000000192bc08dc  + 96\r\n\t33  WebCore                             0x0000000192bc0648  + 212\r\n\t34  WebCore                             0x00000001937301e4  + 232\r\n\t35  WebCore                             0x00000001937302c0  + 56\r\n\t36  WebCore                             0x0000000193693070  + 100\r\n\t37  WebCore                             0x00000001937dfdf0  + 136\r\n\t38  CFNetwork                           0x0000000183bfcf6c  + 128\r\n\t39  CFNetwork                           0x0000000183cc950c  + 104\r\n\t40  CFNetwork                           0x0000000183bebac8  + 76\r\n\t41  CoreFoundation                      0x000000018418ccdc CFArrayApplyFunction + 68\r\n\t42  CFNetwork                           0x0000000183beb974  + 136\r\n\t43  CFNetwork                           0x0000000183beb828  + 312\r\n\t44  CFNetwork                           0x0000000183beb654  + 68\r\n\t45  CoreFoundation                      0x0000000184264240  + 24\r\n\t46  CoreFoundation                      0x00000001842634e4  + 264\r\n\t47  CoreFoundation                      0x0000000184261594  + 712\r\n\t48  CoreFoundation                      0x000000018418d2d4 CFRunLoopRunSpecific + 396\r\n\t49  WebCore                             0x0000000192b88894  + 468\r\n\t50  libsystem_pthread.dylib             0x0000000196303dc8  + 164\r\n\t51  libsystem_pthread.dylib             0x0000000196303d24  + 0\r\n\t52  libsystem_pthread.dylib             0x0000000196300ef8 thread_start + 4\r\n)"}'
data_a = byts.decode().split('\r\n\r\n')



print('data_a', data_a[4])




# import gevent
# import os


# class Parse:
#     def __init__(self, raw_data):
#         self.raw_data = raw_data

#     def get_device_info(self):
#         self.data_temp = self.raw_data.decode().split('\r\n\r\n')
#         self.devcie_info = self.data_temp[2]
#         self.crash_data = self.data_temp[-1]
#         return [self.devcie_info, self.crash_data]

#     def make_cmd(self, cputype, dSYM_folder, app_name):
#         tool = 'atos'
#         option_c = '-arch'
#         option_d = '-o'
#         option_a = '-l'
#         return cmd
