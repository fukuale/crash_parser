# Author = 'Vincent FUNG'
# Create = '2017/09/20'

import socket

HOST = ''
PORT = 8000

text_content = '''
HTTP/1.x 200 OK
Content-Type: text/html

<head>
<title>BEGIN</title>
</head>
<html>
<p>Begin, Python Server</p>
<IMG src="IMG_1648.JPG"/>
</html>
'''

f = open('/Users/vincent/Downloads/IMG_1648.JPG', 'rb')
pic_content = '''
HTTP/1.x 200 OK  
Content-Type: image/jpg
'''

pic_content = pic_content + str(f.read())
f.close()


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST, PORT))

while True:
	pass

	soc.listen(1)

	conn, addr = soc.accept()

	while True:
		request = conn.recv(1024)
		conn.recv.close()
		print('len', len(conn.recv(1024)))
		if not len(request):
			break
		print(request)

	print('reques', request)

	method = request.decode().split()[0]
	print('method', method)

	src = request.decode().split()[1]
	print('src', src)

	if 'POST' in method:
		if 'IMG_1648.JPG' in src:
			print('IMG_1648\n\n\n\n\n\n')
			content = pic_content
		elif src == '/':
			print('post data', request.split())
			content = 'Done'
		else:
			content = text_content

		print('request is :', addr)
		print('connected by', addr)

		conn.sendall(content.encode())

	conn.close()
