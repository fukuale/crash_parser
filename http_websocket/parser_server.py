# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import socket


class Paser_Service(object):
    """docstring for Paser_Service"""

    def __init__(self):
        self.host = ''
        self.port = 7724
        self.buff = bytes()

    def init_socket(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind((self.host, self.port))
        return soc

    def handle_accept(self, soc):
        soc.listen(3)
        conn, addr = soc.accept()
        conn.setblocking(False)
        conn.settimeout(0.2)
        self.receive_data(conn=conn)
        conn.sendall(self.buff)

        conn.close()
        self.buff = bytes()

    def receive_data(self, conn):
        while True:
            try:
                try:
                    raw_package = conn.recv(1024)
                except BlockingIOError as e:
                    pass

                if len(raw_package) == 0:
                    break
                else:
                    self.buff += raw_package

            except Exception as e:
                print('Exception', e)
                break

    # def queop


if __name__ == '__main__':
    ps = Paser_Service()
    socket = ps.init_socket()
    while True:
        ps.handle_accept(socket)
