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
                 ,::,    :# Create = '2017/09/19'Lq@huhao.Li
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

import socket
import time
import subprocess
import gevent

# text_content = 'Done'
text_content = '''

'''

leng = 4388

buff = bytes()

HOST = ''
PORT = 8000

# cmd = atos -arch arm64 -o /Users/vincent.fung/Downloads/WeGamers.app.11311.dSYM/Contents/Resources/DWARF/WeGamers -l 0x00000001000f0000  0x00000001001338ec

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# if exist a TIME_WAIT status port. reuse it.
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

soc.bind((HOST, PORT))

while True:
    soc.listen(1)
    conn, addr = soc.accept()

    conn.setblocking(False)
    conn.settimeout(0.3)
    while True:
        raw_package = bytes()

        try:
            try:

                raw_package = conn.recv(2048)
            except BlockingIOError as e:
                pass

            if len(raw_package) == 0:
                break
            else:
                buff += raw_package

        except Exception as e:
            print('Exception', e)
            break
    print('data', buff)
    conn.sendall(text_content.encode())

    print('\n\n\nclose\n\n\n')

    conn.close()
