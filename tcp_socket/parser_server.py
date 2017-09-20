# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import socket

HOST = ''
PORT = 8000

reply = 'Yes'

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST, PORT))

soc.listen(3)

conn, addr = soc.accept()

request = conn.recv(1024)

print('request is :', addr)
print('connected by', addr)

conn.sendall(reply.encode('utf-8'))

conn.close()
