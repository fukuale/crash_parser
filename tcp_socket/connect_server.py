# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import socket

HOST = '127.0.0.1'
PORT = 8000

request = 'can you hear me?'

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((HOST, PORT))

soc.sendall(request.encode('utf-8'))

reply = soc.recv(1024)

print(reply)

soc.close()