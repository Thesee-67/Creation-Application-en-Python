import socket
if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10000
    message = "Hello"
    client_socket = socket.socket()
    client_socket.connect((host, port))
    client_socket.send(message.encode()) 
    reply = client_socket.recv(1024).decode()
    print("J'ai reçu le message", reply)
    client_socket.close()