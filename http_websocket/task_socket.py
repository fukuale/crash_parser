# Author: Vincent FUNG
# Create: 2018/05/10

import os, time

import zmq
import socket
from multiprocessing import Process, Queue

from task_manager import TaskSchedule

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
            Integer -- The number of the idle port.
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
            port {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        context = zmq.Context()
        _zmq = context.socket(zmq.REP)
        _zmq.bind('tcp://*:7725')
        return _zmq

    @staticmethod
    def return_task():
        return 'processing'

    def socket_communicate(self, _zmq):
        while True:
            msg = _zmq.recv()
            msg = msg.decode().strip()
            if msg != 'get':
                que = Queue()
                ts = TaskSchedule()
                task_run = Process(target=ts.run_parser, args=(que,msg))
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
    