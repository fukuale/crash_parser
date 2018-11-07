# Author: Vincent FUNG
# Create: 2018/05/10

import os
import socket
import time
from multiprocessing import Process, Queue
import sys
import zmq

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
#E:\SourceCode\crash_parser_server

from http_websocket.task_manager import TaskSchedule
from http_websocket.logger import Logger



LOG_FILE = os.path.join(os.path.expanduser('~'), 'CrashParser', 'log', 'CrashParser.log')
LOG = Logger(LOG_FILE, 'SocketServer')


class Task_ZMQ():
    def __init__(self):
        self.ports = [
            7721,
            7722,
            7723,
            7724,
            7725,
            7726
        ]

    def port_use_scan(self):
        """The idle port detection.
        
        Returns:
            [Integer] -- The number of the idle port.
        """
        scan = socket.socket()
        for _port in self.ports:
            if scan.connect_ex(('localhost', _port)) != 0:
                scan.close()
                return _port

    @staticmethod
    def start_socket_server(port):
        """Start socket server.
        
        Arguments:
            port {Integer} -- [The port for socket.]
        
        Returns:
            [zmq.sugar.socket.Socket] -- [zmq.sugar.socket.Socket Instance]
        """
        context = zmq.Context()
        _zmq = context.socket(zmq.REP)
        _zmq.bind('tcp://*:7725')
        return _zmq

    @staticmethod
    def return_task():
        return 'processing'

    def socket_communicate(self, _zmq):
        """socket communicate logic
        
        Arguments:
            _zmq {zmq.sugar.socket.Socket} -- [zmq.sugar.socket.Socket Instance]
        """
        while True:
            msg = _zmq.recv()
            msg = msg.decode().strip()
            LOG.debug(msg)
            if msg != 'get':
                que = Queue()
                ts = TaskSchedule()
                task_run = Process(target=ts.run_parser, args=(que, msg))
                task_run.start()
                while que.empty():
                    time.sleep(0.1)
                _zmq.send_string(str(que.get()))
            elif msg == 'get':
                while que.empty():
                    time.sleep(0.1)
                process = que.get()
                _zmq.send_string(process)

if __name__ == '__main__':
    tz = Task_ZMQ()
    _port = tz.port_use_scan()
    _skt = tz.start_socket_server(_port)
    tz.socket_communicate(_skt)
