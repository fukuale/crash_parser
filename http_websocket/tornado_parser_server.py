# Author = 'Vincent FUNG'
# Create = '2017/09/25'
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
#        :      iuMMP: :,:::,:ii;YRDEBB0viiii:i:iii:i:::iJqL;::
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
#          , :r50EZLEAVEMEALONEP7::::i::,:::::,: :,:,::i;rrririiii::
#              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
#           ,:  :::,: :,,:,,,::::i:i:::::::::::,,:::::iir;ii;7v7;ii;i,
#           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiii;L8OGJrf.r;7:i,
#        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
#         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;:::i:::i:ii:::
#                          _
#                      o _|_           __
#                      |  |      (__| (__) (__(_
#                                   |
import os

from urllib import parse, request

import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.web

from tornado.options import define, options
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

try:
    from task_manager import TaskSchedule
    from logger import Logger
    from init_dsym import DownloadDSYM
    from parse_crash_log import CrashParser
    from get_crash_log import GetCrashInfoFromServer
    from similarity_compare import SimilarityCompute
except ModuleNotFoundError:
    from http_websocket.task_manager import TaskSchedule
    from http_websocket.logger import Logger
    from http_websocket.init_dsym import DownloadDSYM
    from http_websocket.parse_crash_log import CrashParser
    from http_websocket.get_crash_log import GetCrashInfoFromServer
    from http_websocket.similarity_compare import SimilarityCompute

log_file = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
log = Logger(log_file, 'TornadoServer')
define('port', default=7724, type=int)


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('crash_parser_index.html')

    def post(self, *args, **kwargs):
        self.get_argument('crash_log')

    def data_received(self, chunk):
        pass


class ParserHandler(WebSocketHandler):
    def open(self):
        self.write_message('WebSocket has been connected !')
        pass

    def on_close(self):
        log.error('Shocket closed !' + str(self))
        pass

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        if 'guopengzhang' == message:
            try:
                ts = TaskSchedule()
                self.write_message('Trying to parsing... It\'s gonna take a while...')
                ts.parsing()
                self.write_message('Parsing finished. Submiting to JIRA... Wait a moment..')
                ts.jira()
                self.write_message('All Done!')
            except Exception:
                pass
        else:
            self.write_message('Trying to parsing...')
            pl = ParsingLog()
            ap = pl.parsing(message)
            if ap:
                self.write_message(ap)
            else:
                log.error('Nothing return after parsing.' + '\nData in: ' +
                          message + '\nData end.' + 'Parsing return:\n' + ap)
                self.write_message('Parsing content FAILED ! Contact [Vincent FUNG] for support.')

    def check_origin(self, origin):
        return True


class SetWebConf(WebSocketHandler):
    def on_message(self, message):
        pass

class ParsingLog(object):
    def __init__(self):
        self.conf_dir = os.path.join(os.path.expanduser('~'), 'CrashParser', 'conf')
        self.conf_files = [z for a, b, x in os.walk(self.conf_dir) for z in x if
                           not z.startswith('_') and not z.startswith('.')]

    def get_product_name(self, raw_data):
        for k, v in enumerate(self.conf_files):
            if raw_data.find(os.path.splitext(v)[0]) >= 0:
                return os.path.splitext(v)[0]
        else:
            return False

    @staticmethod
    def get_env_info(raw_data):
        env = CrashParser.get_ver_info(raw_data)
        return env, raw_data

    def parsing(self, raw_data):
        p_name = self.get_product_name(raw_data)
        if p_name:
            raw_data = raw_data.encode()
            env, r_data = self.get_env_info(raw_data)
            if env and r_data and raw_data and p_name:
                dd = DownloadDSYM()
                res_dSYM = dd.init_dSYM(version_number=env[0],
                                        build_id=env[1],
                                        version_type=env[-1],
                                        product=p_name)
                if res_dSYM:
                    _ins_parser = CrashParser(productname=p_name, rawdata=raw_data)
                    _data_res = _ins_parser.atos_run(dSYM_file=res_dSYM,
                                                     product_name=p_name,
                                                     tableid=0,
                                                     crash_id='0000000000')
                    if _data_res:
                        return _data_res.replace('<pre>', '').replace('</pre>', '').replace('<', '&lt;').replace('>', '&gt;')
                    else:
                        return 'Look like log losing number of important stack symbols line..'
            else:
                return 'Look like log losing a part of content.'
        else:
            if raw_data.startswith('http') or raw_data.startswith('if'):
                param = dict()
                if raw_data.startswith('http'):
                    if raw_data.find('row=') >= 0:
                        param = {'row': raw_data.split('=')[-1]}
                    else:
                        return 'Incomplete Link. Please paste that what link you can see crash information on browser!'

                elif raw_data.startswith('if'):
                    param = {'row': raw_data}

                parm_encode = parse.urlencode(param).encode('utf-8')

                crash_page = request.Request(
                    url='http://gdata.linkmessenger.com/index.php/Admin/Api/appErrorInfo',
                    data=parm_encode
                )

                crash_content = request.urlopen(crash_page).read()
                if len(crash_content) > 50:
                    return self.parsing(crash_content.decode())
                else:
                    return 'This link address can\'t read any crash information. \nCheck it manully !'
            else:
                return 'Can\'t read environment information from this log content. ' \
                       '\nCheck it manually !\n\n Do not fool me  _(:3 」∠)_'


def run():
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/push_crash", ParserHandler),
        (r"/setwebconf", SetWebConf),
    ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
