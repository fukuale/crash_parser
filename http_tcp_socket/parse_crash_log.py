# Author = 'Vincent FUNG'
# Create = '2017/09/20'
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

import subprocess
import re
import subproc


class CrashParser:
    def __init__(self, cleardata, stacktrac, atospase, packagenames, curname):
        self.nStacktrace_max = 0
        self.stacktrac_list = stacktrac
        self.data_lines = cleardata
        self.parse_lines = atospase
        self.package_names = packagenames
        self.cur_app_name = curname
        self.version_number = str()
        self.build_number = str()
        self.proc = subproc.SubProcessBase()
        self.request_raw = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: 7dbdda4f-8ca2-4a4f-8f0a-6b8feea9e589\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 1779\r\nConnection: keep-alive\r\n\r\n{"data":"\n=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.6.1 (6409) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPhone 6s Plus\nIOS Ver:            iOS 10.2\navailableMemory:    95.2MB\nusedMemory:         100.9MB\ntime:               2017-09-20_23-05-57\nnUid:               2000786930\nsName:              U786930\nsLinkID:            CT1999\nsBindEmail:         418412189@qq.com\nphone:              \nname:              NSGenericException\nreason:             *** Collection <__NSArrayM: 0x170245730> was mutated while being enumerated.\n\ncallStackSymbols:\n0   CoreFoundation                      0x000000018602d1d0  + 148\n1   libobjc.A.dylib                     0x0000000184a6455c objc_exception_throw + 56\n2   CoreFoundation                      0x000000018602cc00  + 0\n3   WeGamers                            0x0000000100f30abc _ZN4Comm17tagSKPBPickleImpl5HFuncERKi + 2117276\n4   WeGamers                            0x00000001004d8214 WeGamers + 4751892\n5   libdispatch.dylib                   0x0000000184eb61fc  + 24\n6   libdispatch.dylib                   0x0000000184eb61bc  + 16\n7   libdispatch.dylib                   0x0000000184ebad68 _dispatch_main_queue_callback_4CF + 1000\n8   CoreFoundation                      0x0000000185fda810  + 12\n9   CoreFoundation                      0x0000000185fd83fc  + 1660\n10  CoreFoundation                      0x0000000185f062b8 CFRunLoopRunSpecific + 444\n11  GraphicsServices                    0x00000001879ba198 GSEventRunModal + 180\n12  UIKit                               0x000000018bf4d7fc  + 684\n13  UIKit                               0x000000018bf48534 UIApplicationMain + 208\n14  WeGamers                            0x000000010006cb04 WeGamers + 117508\n15  libdyld.dylib                       0x0000000184ee95b8  + 4\n"}'
        # self.request_raw = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: 26f012c0-77af-4d2e-a1d2-7713fc3f9db2\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 2386\r\nConnection: keep-alive\r\n\r\n{"data":"\n=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPhone 5 (GSM+CDMA)\nIOS Ver:            iPhone OS 7.1.2\navailableMemory:    22.8MB\nusedMemory:         60.9MB\ntime:               2017-09-20_23-21-26\nnUid:               2007689270\nsName:              U7689270\nsLinkID:            CY89270\nsBindEmail:         \nphone:              \nname:              NSInvalidArgumentException\nreason:             +[UITableViewRowAction rowActionWithStyle:image:handler:size:bgColor:]: unrecognized selector sent to class 0x15567a60\n\ncallStackSymbols:\n0   CoreFoundation                      0x30095ee3  + 154\n1   libobjc.A.dylib                     0x3a830ce7 objc_exception_throw + 38\n2   CoreFoundation                      0x30099703  + 202\n3   CoreFoundation                      0x300980f7  + 706\n4   CoreFoundation                      0x2ffe7058 _CF_forwarding_prep_0 + 24\n5   WeGamers                            0x00bb6a8f WeGamers + 12216975\n6   WeGamers                            0x00bb655d WeGamers + 12215645\n7   WeGamers                            0x0040c355 WeGamers + 4178773\n8   UIKit                               0x32abe94d  + 188\n9   UIKit                               0x328d90b5  + 72\n10  UIKit                               0x32abe88d  + 92\n11  UIKit                               0x32abe033  + 378\n12  UIKit                               0x32a4d3d5  + 816\n13  UIKit                               0x328f7a01  + 148\n14  UIKit                               0x32a5d0af  + 78\n15  UIKit                               0x328f71cb  + 458\n16  UIKit                               0x328f6c2b  + 666\n17  UIKit                               0x328cbe55  + 196\n18  UIKit                               0x328ca521  + 7120\n19  CoreFoundation                      0x30060faf  + 14\n20  CoreFoundation                      0x30060477  + 206\n21  CoreFoundation                      0x3005ec67  + 630\n22  CoreFoundation                      0x2ffc9729 CFRunLoopRunSpecific + 524\n23  CoreFoundation                      0x2ffc950b CFRunLoopRunInMode + 106\n24  GraphicsServices                    0x34f386d3 GSEventRunModal + 138\n25  UIKit                               0x3292a871 UIApplicationMain + 1136\n26  WeGamers                            0x00052c4b WeGamers + 273483\n27  libdyld.dylib                       0x3ad2eab7  + 2\n"}'
        # self.request_raw = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: 07446a36-8e1f-41f7-9888-cf212e9bb59b\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 1762\r\nConnection: keep-alive\r\n\r\n{"data":"\n=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPad 3 (WiFi)\nIOS Ver:            iPhone OS 9.3.5\navailableMemory:    107.7MB\nusedMemory:         116.9MB\ntime:               2017-09-18_20-28-46\nnUid:               2001653270\nsName:              U1653270\nsLinkID:            GJ3270\nsBindEmail:         \nphone:              \nname:              NSRangeException\nreason:             *** -[__NSCFString substringToIndex:]: Index 6 out of bounds; string length 3\n\ncallStackSymbols:\n0   CoreFoundation                      0x23e07933  + 150\n1   libobjc.A.dylib                     0x235a2e17 objc_exception_throw + 38\n2   CoreFoundation                      0x23e07861  + 0\n3   Foundation                          0x2456e58f  + 110\n4   WeGamers                            0x00a5a711 WeGamers + 10118929\n5   WeGamers                            0x00a5a649 WeGamers + 10118729\n6   WeGamers                            0x0019c70f WeGamers + 952079\n7   WeGamers                            0x001a09d7 WeGamers + 969175\n8   Foundation                          0x24625af5 __NSFireDelayedPerform + 468\n9   CoreFoundation                      0x23dca58f  + 14\n10  CoreFoundation                      0x23dca1c1  + 936\n11  CoreFoundation                      0x23dc800d  + 1484\n12  CoreFoundation                      0x23d17229 CFRunLoopRunSpecific + 520\n13  CoreFoundation                      0x23d17015 CFRunLoopRunInMode + 108\n14  GraphicsServices                    0x25307ac9 GSEventRunModal + 160\n15  UIKit                               0x283eb189 UIApplicationMain + 144\n16  WeGamers                            0x000f6c4b WeGamers + 273483\n17  libdyld.dylib                       0x239bf873  + 2\n"}'
        # self.request_raw = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: 68b0a648-5806-4f5d-af4d-0022f213efd3\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 4400\r\nConnection: keep-alive\r\n\r\n{"data":"\n=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPhone 6\nIOS Ver:            iPhone OS 8.3\navailableMemory:    83.5MB\nusedMemory:         66.7MB\ntime:               2017-09-17_15-11-54\nnUid:               0\nsName:              \nsLinkID:            \nsBindEmail:         \nphone:              \n\nERROR: All calls to UIKit need to happen on the main thread. You have a bug in your code. Use dispatch_async(dispatch_get_main_queue(), ^{ ... }); if you\'re unsure what thread you\'re in.\n\nBreak on PSPDFAssertIfNotMainThread to find out where.\n\nStacktrace: (\n\t0   WeGamers                            0x0000000100b84f70 WeGamers + 11226992\n\t1   WeGamers                            0x0000000100b84ff0 WeGamers + 11227120\n\t2   UIKit                               0x00000001891004ac  + 160\n\t3   MediaPlayer                         0x00000001865b3874  + 1108\n\t4   MediaPlayer                         0x00000001865b1fa8  + 240\n\t5   MediaPlayer                         0x00000001865b2034  + 88\n\t6   WebCore                             0x000000019351951c  + 192\n\t7   WebCore                             0x00000001935197f8  + 468\n\t8   WebCore                             0x0000000193518bf8  + 96\n\t9   WebCore                             0x0000000193518b68 _ZN7WebCore19MediaSessionManager13sharedManagerEv + 56\n\t10  WebCore                             0x000000019351766c  + 44\n\t11  WebCore                             0x000000019305733c  + 36\n\t12  WebCore                             0x000000019303fc34  + 1100\n\t13  WebCore                             0x00000001930169a4  + 64\n\t14  WebCore                             0x000000019302b794  + 92\n\t15  WebCore                             0x000000019302b554  + 336\n\t16  WebCore                             0x0000000192b7bf38  + 164\n\t17  WebCore                             0x0000000192b7bd18  + 36\n\t18  WebCore                             0x0000000192b7a61c  + 1924\n\t19  WebCore                             0x0000000192b79048  + 2496\n\t20  WebCore                             0x0000000192b78594  + 136\n\t21  WebCore                             0x0000000192b78440  + 312\n\t22  WebCore                             0x0000000192b77c68  + 140\n\t23  WebCore                             0x0000000192b61f20  + 384\n\t24  WebCore                             0x0000000192bcac68  + 428\n\t25  WebCore                             0x0000000192e785ac  + 116\n\t26  WebCore                             0x0000000192b93bf0 _ZN7WebCore14DocumentLoader10commitDataEPKcm + 64\n\t27  WebKitLegacy                        0x0000000193a2bdb8  + 140\n\t28  WebKitLegacy                        0x0000000193a2bcac  + 76\n\t29  WebKitLegacy                        0x0000000193a2bc40  + 124\n\t30  WebCore                             0x0000000192bc0bf8  + 164\n\t31  WebCore                             0x0000000192bc0a80 _ZN7WebCore14DocumentLoader12dataReceivedEPNS_14CachedResourceEPKci + 348\n\t32  WebCore                             0x0000000192bc08dc  + 96\n\t33  WebCore                             0x0000000192bc0648  + 212\n\t34  WebCore                             0x00000001937301e4  + 232\n\t35  WebCore                             0x00000001937302c0  + 56\n\t36  WebCore                             0x0000000193693070  + 100\n\t37  WebCore                             0x00000001937dfdf0  + 136\n\t38  CFNetwork                           0x0000000183bfcf6c  + 128\n\t39  CFNetwork                           0x0000000183cc950c  + 104\n\t40  CFNetwork                           0x0000000183bebac8  + 76\n\t41  CoreFoundation                      0x000000018418ccdc CFArrayApplyFunction + 68\n\t42  CFNetwork                           0x0000000183beb974  + 136\n\t43  CFNetwork                           0x0000000183beb828  + 312\n\t44  CFNetwork                           0x0000000183beb654  + 68\n\t45  CoreFoundation                      0x0000000184264240  + 24\n\t46  CoreFoundation                      0x00000001842634e4  + 264\n\t47  CoreFoundation                      0x0000000184261594  + 712\n\t48  CoreFoundation                      0x000000018418d2d4 CFRunLoopRunSpecific + 396\n\t49  WebCore                             0x0000000192b88894  + 468\n\t50  libsystem_pthread.dylib             0x0000000196303dc8  + 164\n\t51  libsystem_pthread.dylib             0x0000000196303d24  + 0\n\t52  libsystem_pthread.dylib             0x0000000196300ef8 thread_start + 4)\n"}'
        # self.request_raw = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: bac5bc9a-80af-42ec-9517-2228212b2bd0\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/6.3.2\r\nAccept: */*\r\nHost: 192.168.1.104:8000\r\naccept-encoding: gzip, deflate\r\ncontent-length: 2442\r\nConnection: keep-alive\r\n\r\n{"data":"\n=============\xe5\xbc\x82\xe5\xb8\xb8\xe5\xb4\xa9\xe6\xba\x83\xe6\x8a\xa5\xe5\x91\x8a=============\nversion:            V1.9.5 (11311) [\xe6\xad\xa3\xe5\xbc\x8f\xe7\x89\x88]\ndeviceType:         iPhone 5s (GSM+CDMA)\nIOS Ver:            iOS 10.3.3\navailableMemory:    331.9MB\nusedMemory:         97.1MB\ntime:               2017-09-18_09-50-15\nnUid:               2007233192\nsName:              U7233192\nsLinkID:            CU33192\nsBindEmail:         \nphone:              \nname:              NSInvalidArgumentException\nreason:             *** -[__NSPlaceholderDictionary initWithObjects:forKeys:count:]: attempt to insert nil object from objects[0]\n\ncallStackSymbols:\n0   CoreFoundation                      0x0000000181b86ff8  + 148\n1   libobjc.A.dylib                     0x00000001805e8538 objc_exception_throw + 56\n2   CoreFoundation                      0x0000000181a6d9b4  + 364\n3   CoreFoundation                      0x0000000181a6d824  + 64\n4   WeGamers                            0x0000000100cafa84 WeGamers + 13204100\n5   WeGamers                            0x000000010014426c WeGamers + 1229420\n6   WeGamers                            0x000000010035d6a0 WeGamers + 3430048\n7   WeGamers                            0x0000000100aad4f8 WeGamers + 11097336\n8   UIKit                               0x0000000187cedc54  + 96\n9   UIKit                               0x0000000187cedbd4  + 80\n10  UIKit                               0x0000000187cd8148  + 440\n11  UIKit                               0x0000000187ced4b8  + 576\n12  UIKit                               0x0000000187cecfd4  + 2480\n13  UIKit                               0x0000000187ce836c  + 3192\n14  UIKit                               0x0000000187cb8f80  + 340\n15  UIKit                               0x00000001884b2a20  + 2400\n16  UIKit                               0x00000001884ad17c  + 4268\n17  UIKit                               0x00000001884ad5a8  + 148\n18  CoreFoundation                      0x0000000181b3542c  + 24\n19  CoreFoundation                      0x0000000181b34d9c  + 540\n20  CoreFoundation                      0x0000000181b329a8  + 744\n21  CoreFoundation                      0x0000000181a62da4 CFRunLoopRunSpecific + 424\n22  GraphicsServices                    0x00000001834cd074 GSEventRunModal + 100\n23  UIKit                               0x0000000187d1dc9c UIApplicationMain + 208\n24  WeGamers                            0x000000010005b8ec WeGamers + 276716\n25  libdyld.dylib                       0x0000000180a7159c  + 4\n"}'
    # Split request raw data to get the request body
    def get_crash_info_raw(self):
        request_data = self.request_raw.decode().split('\r\n\r\n')
        return request_data[-1]

    # Split request body to get crash information list
    def get_crash_info(self, pkgname):

        data = self.get_crash_info_raw()
        # Get application name
        for k, v in enumerate(pkgname):
            if v in data:
                self.cur_app_name = k
        # Split '\n' to get lines
        self.data_lines = data.split('\n')
        # Remove first and last one. These was the json indicator.
        # Because i can not transfer the bytes to json now.. maybe later can..
        del self.data_lines[0]
        del self.data_lines[-1]
        # Get the count number of the Stacktrace list items
        print('try get self.nStacktrace_max_b', self.data_lines[-1].split()[0])
        self.nStacktrace_max = int(self.data_lines[-1].split()[0]) + 2

    def get_env_info(self):
        # Complier regular expression
        ver = re.compile(r'\d+(\.\d+){0,2}')    # version code
        biu = re.compile(r'[\d]+')              # Consecutive numbers
        typ = re.compile(r'[\u4e00-\u9fa5]+')   # Match chinese
        for i in self.data_lines:
            if 'version' in i:
                version_code = ver.search(i)
                build_number = biu.findall(i)
                if typ.findall(i)[0] == '正式版':
                    print('正式版', typ.findall(i))
                    version_type = 'appstore'
                else:
                    print('dev版', typ.findall(i))
                    version_type = 'dev'
                return [version_code.group(0), build_number[-1], version_type]

    def is_32bit(self):
        if len(self.data_lines[-5].split()[2]) == 10:

            return 'armv7'
        else:
            return 'arm64'

    # Get Stacktrac list and seqencing.
    def get_crash_list(self):
        print('self.nStacktrace_max', self.nStacktrace_max)
        for i in range(1, self.nStacktrace_max):
            # Get lines negative number.
            _index = i - i * 2
            # Get list data by reverstion.
            self.stacktrac_list.append(self.data_lines[_index].split())

    def call_atos(self, dSYM_file, product_name, proc):
        # Splicing the dSYM absolute location \
        # to get the application binary absolute location on dSYM file.
        atos = 'atos'
        arch = '-arch'
        op = '-o'
        _l = '-l'
        app_symbol = dSYM_file + '/Contents/Resources/DWARF/%s' % product_name
        print('app_symbol', app_symbol)

        # call addr_list to filter what data need to parsing.
        self.addr_list(produce_name=product_name)

        # Get cpu arch
        cpu_arm_ = self.is_32bit()
        print('parse_line', self.parse_lines)

        # enumerate wait to parsing data
        for _index, _value in enumerate(self.parse_lines):
            print('enumerate', _index, _value)

            # Pick memory address
            line_id = (_value[0] + 1) - 2 * (_value[0] + 1)
            line_id_raw = _value[1]
            produce_name_raw = _value[2]
            memory_addr = _value[3]
            base_addr = _value[4]
            offset = _value[-1]
            # Parsing memory address to get the truth method called
            atos_cmd = ' '.join([
                atos, arch, cpu_arm_, op, app_symbol,
                _l, base_addr, memory_addr])
            print(atos_cmd)
            parse_result = self.proc.sub_procs_run(cmd=atos_cmd)
            result = parse_result.stdout.decode()
            # Replace result to finally data
            replace_data = '    '.join([
                line_id_raw, produce_name_raw, memory_addr, offset, result])
            print('replace_data', 'target line', line_id, 'data:\n',replace_data)
            print('self.data_lines[line_id]', self.data_lines[line_id])
            self.data_lines[line_id] = replace_data

        # print the finally data after parsing
        print('\n'.join(self.data_lines))

    def addr_list(self, produce_name):
        self.get_crash_list()
        print('self.stacktrac_list', self.stacktrac_list)
        for key, line in enumerate(self.stacktrac_list):
            print('enumerate(self.stacktrac_list', key, line)

            if produce_name in line:
                _memory_addr_start = hex(
                    int('%s' % line[2], 16) - int(line[-1]))
                _memory_addr_stack = line[2]
                less_line = [key, line[0], line[1],
                             _memory_addr_stack, _memory_addr_start, line[-1]]
                self.parse_lines.append(less_line)
