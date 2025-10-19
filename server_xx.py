
from socket import *
from threading import *

HOST = '127.0.0.1'
PORT = 8080

clients = []

def notification(data, exclude_socket=None):
   for client in clients:
       if client != exclude_socket:
           try:
               client.sendall(data)
           except:
               pass

def client_handler(client_socket):
   while True:
       try:
           data = client_socket.recv(4096)
           if not data:
               break
           notification(data, exclude_socket=client_socket)
       except:
           break
   if client_socket in clients:
       clients.remove(client_socket)
   client_socket.close()

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'Сервер запущено на {HOST}:{PORT}')

while True:
    client_socket, addr = server_socket.accept()
    print(f'Підключився клієнт: {addr}')
    clients.append(client_socket)

    t = Thread(target=client_handler, args=(client_socket,))
    t.start()