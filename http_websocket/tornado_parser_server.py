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
from task_manager import TaskSchedule
from logger import Logger

LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'TornadoServer')
define('port', default=7724, type=int)


class IndexHandler(RequestHandler):
    """
    Render page
    """
    def get(self, *args, **kwargs):
        self.render('crash_parser_index.html')

    def post(self, *args, **kwargs):
        self.get_argument('crash_log')

    def data_received(self, chunk):
        pass


class ParserHandler(WebSocketHandler):
    """
    Parse http request
    """
    def open(self):
        self.write_message('WebSocket has been connected !')

    def on_close(self):
        LOG.error('Shocket closed !' + str(self))

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        if message:
            task_schle = TaskSchedule()
            data = task_schle.run_parser(raw_data=message.strip())
            if data:
                self.write_message(str(data))
        else:
            self.write_message('No content was submit.')

    def check_origin(self, origin):
        return True


class SetWebConf(WebSocketHandler):
    """[summary]
    """
    def on_message(self, message):
        pass


def run():
    """
    call
    """
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        [
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
