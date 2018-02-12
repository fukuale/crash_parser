# Author = 'Vincent FUNG'
# Create = '2017/09/25'

import os

import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.web

import zmq

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
        # Start ZMQ socket client.
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.bind("tcp://*:7725")
        # Object validation.
        if len(message) > 0:
            # Transfer object type to string to send.
            if isinstance(message, bytes):
                message = message.decode()
            elif isinstance(message, int):
                message = str(message)
            elif isinstance(message, str):
                pass
            else:
                self.write_message('Unknow data. type %s ' % type(message))        
            socket.send_string(message)
            # Receive handle result.
            result = socket.recv()
            print(result)
            if isinstance(result, bytes):
                result = result.decode()
            if result == "Finish":
                self.write_message("Parse finished.")
            else:
                self.write_message(str(result))



            # task_schle = TaskSchedule()
            # data = task_schle.run_parser(raw_data=message.strip())
            # if result:
            #     self.write_message(str(result))
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

    # context = zmq.Context.instance()
    # socket = context.socket(zmq.REP)
    # socket.bind("tcp://*:7725")


if __name__ == '__main__':
    run()
