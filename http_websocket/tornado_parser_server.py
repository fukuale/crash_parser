# Author = 'Vincent FUNG'
# Create = '2017/09/25'

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import zmq
from tornado.options import define, options
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from http_websocket.logger import Logger
from http_websocket.task_manager import TaskSchedule

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
        # Define the data valid
        valid = int()
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:7725")
        # Object validation.
        if len(message) > 0:
            # Transfer object type to string to send.
            if isinstance(message, bytes):
                message = message.decode()
                valid = 1
            elif isinstance(message, int):
                message = str(message)
                valid = 1
            elif isinstance(message, str):
                valid = 1
            else:
                self.write_message('Unknow data. type %s ' % type(message))
            LOG.debug(message)
            if valid:
                socket.send_string(str(message))       #将消息发送到7725端口
                childpid = socket.recv()
                msg = ' '.join(['='*20, ('Process %s Started!' % childpid.decode()).center(25, ' '), '='*20])
                self.write_message(msg)
                while valid:
                    socket.send_string('get')
                    data = socket.recv()
                    if data.decode() == 'Finish':
                        msg = ' '.join(['='*20, ('Process %s Finish!' % childpid.decode()).center(25, ' '), '='*20])
                        self.write_message(msg)
                        valid = 0
                    else:
                        self.write_message(data)
        else:
            self.write_message('No content was submit.')

    def check_origin(self, origin):
        return True     # 允许WebSocket的跨域请求


class SetWebConf(WebSocketHandler):
    """Useless now.
    
    Arguments:
        WebSocketHandler {[type]} -- [description]
    """
    def on_message(self, message):
        pass


def run():
    """
    Start tornado server.
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
