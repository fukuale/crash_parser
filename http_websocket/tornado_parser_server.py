# Author = 'Vincent FUNG'
# Create = '2017/09/25'

import os

import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.web

from tornado.options import define, options
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from multiprocessing import Queue, Process


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
        if message:
            ts = TaskSchedule()
            data = ts.run_parser(raw_data=message.strip())
            if data:
                self.write_message(data)
        else:
            self.write_message('No content was submit.')

    def check_origin(self, origin):
        return True


class SetWebConf(WebSocketHandler):
    def on_message(self, message):
        pass


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
