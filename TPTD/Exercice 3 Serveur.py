import socket

if __name__ == '__main__':
    port = 10000
    reply = "Bonjour"

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    print("Je me connecte")
    server_socket.listen(1)
    conn, address = server_socket.accept()
    message = conn.recv(1024).decode()
    print("J'ai reçus le message", message)
    conn.send(reply.encode())
    print("J'ai envoyé le message", reply)
    conn.close() 
    server_socket.close()
    print("je termine la conversation")